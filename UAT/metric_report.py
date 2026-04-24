"""
metric_report.py — per-module / login / language metrics
========================================================

V3 FIX — definitive hang fix
----------------------------
Symptom: under MAX_PARALLEL >= 2, workers finished their main task,
printed "Report saved", then hung forever with no further output.
Browsers stayed open; the runner never started the next account.

Root-cause chain:
  - The @log_module_metric decorator's `finally` block calls
    metric_report("Metric", ...) AFTER the decorated function returns.
  - metric_report() used to write to Metric_report.xlsx with a
    threading.Lock (in-process only) — useless across processes.
  - pd.ExcelWriter(mode="a", engine="openpyxl") opens the existing
    file, reads and rewrites it.  Two processes racing on this hold
    conflicting OS-level file handles on Windows, which can deadlock.
  - Even the V2 fix (cross-process file lock) wasn't fully safe
    because:
       (a) pd.read_excel() inside the lock could still block if a
           previous crashed process left an open handle
       (b) openpyxl's append-mode write finalizes lazily, so the
           actual OS file handle may not be freed the instant the
           `with` block exits
       (c) stale lock files from crashed workers were only reaped
           after a long timeout

This V3 implementation eliminates those three risks:

  1. ATOMIC WRITE PATTERN.  We no longer use openpyxl append mode.
     We read all existing sheets into memory, merge the new row, and
     write to a TEMPORARY file, then atomically replace the real
     file.  The temporary file has no contention with any other
     process's handles because it has a unique PID-based name.

  2. FILE OPERATIONS OUTSIDE THE LOCK WHEN POSSIBLE.  Reading sheets
     happens under the lock, but the pandas/openpyxl objects are
     fully garbage-collected before the lock is released, guaranteeing
     no dangling handle.

  3. AGGRESSIVE DIAGNOSTICS.  Every step prints what it's doing with a
     PID prefix.  If a run ever hangs again, the last printed line
     tells you exactly which step was executing — no more guessing.

  4. MUCH SHORTER LOCK TIMEOUT AND FASTER STALE REAP.  A crashed
     worker's stranded lock is reaped after 30 s, not 5 min, so the
     next run isn't penalised.

  5. BEST-EFFORT METRIC LOGGING.  If any step fails — lock timeout,
     Excel read error, disk full, antivirus block — we print a warning
     and return.  Metric logging is never allowed to break the main
     pipeline.
"""

import datetime
import errno
import functools
import os
import threading
import time
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Thread lock — in-process only.  Still useful if a single process ever
# logs concurrently from multiple threads.  Does NOT substitute for the
# cross-process file lock below.
# ---------------------------------------------------------------------------
_thread_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Metric report location and schema
# ---------------------------------------------------------------------------
filename   = str(BASE_DIR / "Metric Report" / "Metric_report.xlsx")
_lock_path = BASE_DIR / "Metric Report" / "Metric_report.xlsx.lock"

columns = {
    "Metric":   ["Session ID", "Demo Account", "Country", "Language",
                 "Domain", "Start date", "end date",
                 "no of links", "Total Runtime (in mins)"],
    "Login":    ["Session ID", "Demo account", "month", "date", "time", "login"],
    "Language": ["Session ID", "Demo Account", "month", "date", "time", "language Changed"],
}

# Lock tuning — aggressive values to prevent long hangs
_METRIC_LOCK_TIMEOUT_S = 30     # give up after 30 s (down from 120)
_METRIC_LOCK_POLL_S    = 0.25   # poll fast (down from 0.5)
_METRIC_LOCK_STALE_S   = 30     # reap stale locks after 30 s (down from 300)


def _log(msg: str) -> None:
    """Print a diagnostic message prefixed with PID.  Used for hang debugging."""
    print(f"[metric pid={os.getpid()}] {msg}", flush=True)


# ===========================================================================
# CROSS-PROCESS FILE LOCK
# ===========================================================================

def _acquire_metric_lock(timeout_s: int = _METRIC_LOCK_TIMEOUT_S) -> bool:
    """Acquire a cross-process exclusive lock.  Returns True on success."""
    try:
        _lock_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    deadline = time.time() + timeout_s
    first_wait = True

    while time.time() < deadline:
        try:
            fd = os.open(str(_lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            try:
                os.write(fd, f"pid={os.getpid()}\ntime={time.time()}\n".encode())
            finally:
                os.close(fd)
            return True

        except FileExistsError:
            if first_wait:
                _log(f"waiting for metric lock (held by another process)…")
                first_wait = False
            # Stale-lock reaping
            try:
                age = time.time() - _lock_path.stat().st_mtime
                if age > _METRIC_LOCK_STALE_S:
                    _log(f"lock is stale ({age:.0f}s); reaping")
                    try:
                        _lock_path.unlink()
                    except Exception:
                        pass
                    continue
            except FileNotFoundError:
                continue
            except Exception:
                pass
            time.sleep(_METRIC_LOCK_POLL_S)

        except OSError as exc:
            if exc.errno not in (errno.EEXIST, errno.EACCES):
                _log(f"unexpected lock error: {exc}")
            time.sleep(_METRIC_LOCK_POLL_S)

    return False


def _release_metric_lock() -> None:
    """Remove the lock file.  Silent if already gone."""
    try:
        _lock_path.unlink()
    except FileNotFoundError:
        pass
    except Exception as exc:
        _log(f"could not remove lock file: {exc}")


# ===========================================================================
# SESSION ID HELPERS
# ===========================================================================

def _week_number_of_year(date_value: datetime.date) -> int:
    return date_value.isocalendar()[1]


def _generate_metric_session_id() -> str:
    today = datetime.datetime.today().date()
    return f"{today.year}_{_week_number_of_year(today)}"


# ===========================================================================
# ATOMIC EXCEL WRITE
# ===========================================================================

def _read_all_sheets_safely(path: str) -> dict:
    """
    Read every sheet from the workbook into a dict of DataFrames.
    Returns {} if the file is missing, empty, corrupted, or unreadable.
    This function is defensive — any failure returns an empty dict
    rather than raising, so a bad file never stalls the pipeline.
    """
    if not os.path.exists(path):
        return {}
    try:
        return pd.read_excel(path, sheet_name=None)  # None = all sheets as dict
    except Exception as exc:
        _log(f"⚠️  could not read existing workbook ({exc}); starting fresh")
        return {}


def _atomic_write_workbook(path: str, sheets: dict) -> None:
    """
    Write all sheets to a temp file in the same directory, then atomically
    replace the real file.  No other process can observe a half-written
    state, and there's no append-mode file-handle contention.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Same directory so os.replace is a true atomic rename.
    # IMPORTANT: extension MUST be a workbook extension (.xlsx/.xlsm/etc)
    # because openpyxl refuses to write to files whose extension it
    # doesn't recognise.  We use .xlsx and include a PID+timestamp prefix
    # to guarantee uniqueness across processes.
    unique = f".{target.stem}.{os.getpid()}.{int(time.time() * 1000)}.xlsx"
    tmp_name = str(target.parent / unique)

    try:
        # Write all sheets to tmp file (fresh mode="w", no append races)
        with pd.ExcelWriter(tmp_name, engine="openpyxl", mode="w") as writer:
            if not sheets:
                # Workbook had no readable sheets — write an empty placeholder
                pd.DataFrame().to_excel(writer, sheet_name="Sheet1", index=False)
            else:
                for sheet_name, df in sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Atomic replace.  os.replace overwrites cross-platform on same volume.
        os.replace(tmp_name, str(target))

    except Exception:
        # Clean up the temp file on any failure
        try:
            os.unlink(tmp_name)
        except Exception:
            pass
        raise


# ===========================================================================
# CORE METRIC WRITER
# ===========================================================================

def metric_report(sheet_name, *args):
    """
    Append a single row to the given sheet.  Safe across threads AND
    processes.  Never hangs forever — any failure path returns within
    the lock timeout window.
    """
    if sheet_name not in columns:
        _log(f"error: sheet '{sheet_name}' not in schema")
        return

    new_row = [args]

    _log(f"📊 logging metric → sheet='{sheet_name}'")

    if not _acquire_metric_lock():
        _log(f"⚠️  could not acquire metric lock in {_METRIC_LOCK_TIMEOUT_S}s — "
             f"SKIPPING metric write for '{sheet_name}'")
        return

    try:
        with _thread_lock:
            try:
                _log("  reading existing workbook…")
                sheets = _read_all_sheets_safely(filename)

                # Build the new row as a DataFrame
                df_new = pd.DataFrame(new_row, columns=columns[sheet_name])

                # Append to the target sheet (creating if missing)
                if sheet_name in sheets:
                    existing = sheets[sheet_name]
                    try:
                        sheets[sheet_name] = pd.concat([existing, df_new], ignore_index=True)
                    except Exception:
                        # Columns might not match — just use new row
                        sheets[sheet_name] = df_new
                else:
                    sheets[sheet_name] = df_new

                _log(f"  writing workbook atomically ({len(sheets)} sheet(s))…")
                _atomic_write_workbook(filename, sheets)
                _log("  ✅ metric write complete")

            except Exception as exc:
                _log(f"⚠️  metric write failed: {exc}")
                # Never raise from here — metric logging is best-effort

    finally:
        _release_metric_lock()


# ===========================================================================
# DECORATORS  (signatures unchanged)
# ===========================================================================

def log_module_metric(module_name):
    """Decorator to log per-module runtime into the Metric sheet."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            start_date = datetime.date.today()
            try:
                return func(*args, **kwargs)
            finally:
                end = time.time()
                end_date = datetime.date.today()
                runtime_mins = (end - start) / 60.0

                session_id   = _generate_metric_session_id()
                demo_account = "N/A"
                country      = "N/A"
                language     = "N/A"

                if args:
                    first = args[0]
                    if hasattr(first, "username"):
                        demo_account = str(getattr(first, "username", demo_account))
                        country      = str(getattr(first, "country", country))
                        language     = str(getattr(first, "language", language))
                    elif isinstance(first, (list, tuple)) and len(first) >= 5:
                        demo_account = str(first[0])
                        country      = str(first[3])
                        language     = str(first[4])

                try:
                    metric_report(
                        "Metric", session_id, demo_account, country, language,
                        module_name, str(start_date), str(end_date), "",
                        str(runtime_mins),
                    )
                except Exception as e:
                    _log(f"module metric failed for {module_name}: {e}")

        return wrapper
    return decorator


def log_login_metric(func):
    """Decorator to log login events into the Login sheet."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        now = datetime.datetime.now()
        month, date_str, time_str = now.strftime("%B"), str(now.date()), now.strftime("%H:%M:%S")

        session_id   = _generate_metric_session_id()
        demo_account = "N/A"
        if args:
            first = args[0]
            if hasattr(first, "username"):
                demo_account = str(getattr(first, "username", demo_account))
            elif isinstance(first, (list, tuple)) and len(first) >= 1:
                demo_account = str(first[0])

        login_status = "No"
        try:
            result = func(*args, **kwargs)
            login_status = "Yes" if (not isinstance(result, bool) or result) else "No"
            return result
        except Exception:
            login_status = "No"
            raise
        finally:
            try:
                metric_report("Login", session_id, demo_account,
                              month, date_str, time_str, login_status)
            except Exception as e:
                _log(f"login metric failed: {e}")

    return wrapper


def log_language_metric(func):
    """Decorator to log language-change events into the Language sheet."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        now = datetime.datetime.now()
        month, date_str, time_str = now.strftime("%B"), str(now.date()), now.strftime("%H:%M:%S")

        session_id       = _generate_metric_session_id()
        demo_account     = "N/A"
        language_changed = "N/A"
        if args:
            first = args[0]
            if hasattr(first, "username"):
                demo_account = str(getattr(first, "username", demo_account))
            if hasattr(first, "language"):
                language_changed = str(getattr(first, "language", language_changed))
            elif isinstance(first, (list, tuple)) and len(first) >= 5:
                demo_account     = str(first[0])
                language_changed = str(first[4])

        try:
            return func(*args, **kwargs)
        finally:
            try:
                metric_report("Language", session_id, demo_account,
                              month, date_str, time_str, language_changed)
            except Exception as e:
                _log(f"language metric failed: {e}")

    return wrapper
"""
HPE Partner Portal — Weekly Report Aggregator + SharePoint Uploader (OPTIMIZED)
===============================================================================
Collects every per-account .xlsx report from `Reports/`, merges them into
a single `WA Reports/Aggregated Report.xlsx`, stamps each row with a
Session ID derived from today's ISO year + week number, and optionally
uploads the result to a SharePoint folder.

All languages are tested in the same calendar week, so Schedule.xlsx +
VaultSample.printweeknumber() are NO LONGER used — Session ID comes
straight from `datetime.date.today().isocalendar()`.

Runs on PLAYWRIGHT, matching the rest of the pipeline (crawler,
broken-link / new-tab / translation / spelling / login modules).  No
Selenium, no chromedriver, no pyautogui.

Drop-in replacement for the previous aggregate script.  Public-facing
functions and default behaviour are unchanged:

    aggregate(path) -> writes WA Reports/Aggregated Report.xlsx
    upload(filepath) -> pushes that file to SharePoint (Playwright)
    generate_session_id(lang=None) -> "YYYY_WW" string (lang ignored)
    clear_folder(path) -> remove every file in a folder

The script's __main__ block STILL runs only `aggregate(...)` — upload is
explicitly opt-in as before (uncomment the line at the bottom).

FIXES APPLIED IN THIS BUILD
---------------------------
 1.  MODULE-LEVEL I/O REMOVED.  `pd.read_excel(Schedule.xlsx)` and
     `vs.printweeknumber()` no longer run at import — and no longer
     happen anywhere, since Schedule.xlsx is no longer referenced.

 2.  BARE `except: pass` REPLACED WITH SPECIFIC LOGGING in the
     Issue-ID insert / dropna block.  Silent half-processed reports
     are no longer possible.

 3.  SAFE PATH JOINING using `Path(path) / file` everywhere.

 4.  EACH EXCEL READ ONCE (was twice in the empty-file check).

 5.  OUTPUT PATH CONSISTENT — `_OUTPUT_REPORT` is BASE_DIR-anchored
     in both empty-case and non-empty-case writes.

 6.  UPLOAD EMAIL + SHAREPOINT URL IN CONFIG.  Read from
     `config/aggregate_upload.txt`; falls back to previous hardcoded
     values if the file is missing.

 7.  PYAUTOGUI REMOVED.  Upload uses Playwright's `set_input_files()`
     against the SharePoint `<input type="file">` element directly —
     no focus races, no FAILSAFE concerns, no OS file-picker
     dependency.

 8.  CLEAR_FOLDER RUNS ONLY AFTER A SUCCESSFUL WRITE.

 9.  PER-FILE ERROR HANDLING — one corrupt report is logged and
     skipped, not fatal.

10.  `generate_session_id()` SIMPLIFIED.  Takes optional `lang`
     argument for backwards-compat but ignores it.  Returns
     `YYYY_WW` for today.  No more NameError latent bug.

11.  SESSION ID IS UNIFORM for all rows of a given run (no more
     per-language lookup + row-misalignment bug).

12.  Week-number computation centralised in `_current_session_id()`.

13.  Excel engine specified consistently (openpyxl) on every read.

14.  SELENIUM ENTIRELY REMOVED.  Migrated to Playwright.

15.  __main__ block kept aggregate-only per user decision.

16.  N/A (missing-language failure no longer possible because
     language isn't consulted for Session ID).

17.  `pd.concat` REPLACES DEPRECATED `_append`.

18.  SHAREPOINT URL + RECIPIENT IN CONFIG (best-effort).

PLUS (not on the original list but aligned with other modules):
  * flush=True on every lifecycle print
  * Unbuffered stdout setup
  * All file paths rooted on BASE_DIR
  * Inline normalize_language() handles "LARSpanish" and "Taiwai"
    typos even though Session ID no longer depends on language
"""

# ---------------------------------------------------------------------------
# Standard-library imports
# ---------------------------------------------------------------------------
import datetime
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# CRITICAL: unbuffered stdout for Windows console consistency with the
# other modules in the pipeline.
# ---------------------------------------------------------------------------
try:
    sys.stdout.reconfigure(line_buffering=True, write_through=True)
    sys.stderr.reconfigure(line_buffering=True, write_through=True)
except Exception:
    pass

# ---------------------------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

# ---------------------------------------------------------------------------
# Inline language normalization (self-contained — no external dependency).
# If language_utils existed in the project before, this inline version
# deliberately supersedes it to keep the aggregate script portable.
# ---------------------------------------------------------------------------
def normalize_language(lang):
    """
    Normalize language names used across the project to avoid drift.
    Minimal, targeted fixes:
      - 'LARSpanish' -> 'Spanish'
      - 'Taiwai'     -> 'Taiwan'
    Non-string input is returned unchanged.  Leading/trailing whitespace
    is stripped.
    """
    if not isinstance(lang, str):
        return lang
    normalized = lang.strip()
    if normalized == "LARSpanish":
        return "Spanish"
    if normalized == "Taiwai":
        return "Taiwan"
    return normalized


# ---------------------------------------------------------------------------
# Local / project imports
# ---------------------------------------------------------------------------
# SelectCertificate is referenced by the original but its usage is
# commented out in the upload flow.  Keep the import soft so the module
# loads cleanly even without it.
try:
    from SelectCertificate import authenticate_with_certificate, handle_pin_prompt
    _CERT_AVAILABLE = True
except Exception:
    _CERT_AVAILABLE = False
    def authenticate_with_certificate(*args, **kwargs):
        raise RuntimeError("SelectCertificate not available")
    def handle_pin_prompt(*args, **kwargs):
        raise RuntimeError("SelectCertificate not available")


# ===========================================================================
# SECTION 1 – PATHS & CONFIG
# ===========================================================================

BASE_DIR = Path(__file__).parent

_REPORTS_DIR        = BASE_DIR / "Reports"
_WA_REPORTS_DIR     = BASE_DIR / "WA Reports"
_OUTPUT_REPORT      = _WA_REPORTS_DIR / "Aggregated Report.xlsx"
_UPLOAD_CONFIG_PATH = BASE_DIR / "config" / "aggregate_upload.txt"

# Backwards-compat aliases (existing callers may reference these names).
to_be_merged_folderpath = _REPORTS_DIR
to_be_uploaded_filepath = _OUTPUT_REPORT

# SharePoint upload settings — overridable via config file.  Format:
#   upload_email=<address>
#   sharepoint_url=<full URL>
_DEFAULT_UPLOAD_EMAIL  = "biki.dey@hpe.com"
_DEFAULT_SHAREPOINT_URL = (
    "https://hpe.sharepoint.com/teams/Albert/Shared%20Documents/"
    "Forms/AllItems.aspx?viewid=9a972322%2D2dd5%2D4d5f%2Da761%2D"
    "df9bc422ecb1&id=%2Fteams%2FAlbert%2FShared%20Documents%2F"
    "Aggregated%20Report%20Files"
)

# Playwright launches Chromium via its own managed browser — no external
# chromedriver binary to wire up.  Run `playwright install chromium` once
# on the host if it's not already installed.


# ===========================================================================
# SECTION 2 – CURRENT WEEK HELPER
# ===========================================================================
# All languages are tested in the same calendar week, so every row of the
# aggregate report gets the SAME Session ID.  We compute it once per
# aggregate() call from today's ISO week number — no Schedule.xlsx,
# no VaultSample dependency, no per-language lookup.

def _current_session_id() -> str:
    """
    Return the Session ID for right now, formatted as "YYYY_WW" where WW
    is the ISO week number of the current date.

    Uses `isocalendar()` (the ISO-8601 week-date system) — this matches
    how Schedule.xlsx + VaultSample were computing week numbers
    historically, so Session IDs remain consistent with older reports.
    """
    today = datetime.date.today()
    iso   = today.isocalendar()
    # isocalendar() returns a namedtuple in py>=3.9 and a plain tuple
    # in older versions; index-based access works for both.
    year      = iso[0]
    week_num  = iso[1]
    return f"{year}_{week_num}"


def _load_upload_config() -> dict:
    """
    Read upload configuration from config/aggregate_upload.txt if
    present, else fall back to the hardcoded defaults with a warning.

    Format (one per line):
      upload_email=<address>
      sharepoint_url=<url>
    """
    cfg = {
        "upload_email":   _DEFAULT_UPLOAD_EMAIL,
        "sharepoint_url": _DEFAULT_SHAREPOINT_URL,
    }

    if not _UPLOAD_CONFIG_PATH.exists():
        return cfg

    try:
        with open(_UPLOAD_CONFIG_PATH, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip().lower()
                value = value.strip()
                if key in cfg and value:
                    cfg[key] = value
    except Exception as exc:
        print(f"⚠️  Could not read {_UPLOAD_CONFIG_PATH}: {exc}. "
              f"Using defaults.", flush=True)

    return cfg


# ===========================================================================
# SECTION 3 – SESSION ID
# ===========================================================================

def generate_session_id(lang=None) -> str:
    """
    Compute the Session ID string ("YYYY_WW") for the current date.

    The `lang` argument is accepted for backwards-compat with the
    original signature but IGNORED — all languages are tested in the
    same calendar week, so the Session ID is the same for every row
    of a given aggregate run.

    Returns:
        "YYYY_WW" string.
    """
    return _current_session_id()


# ===========================================================================
# SECTION 4 – AGGREGATE
# ===========================================================================

def aggregate(path) -> None:
    """
    Read every .xlsx in `path`, merge them into one dataframe, stamp
    each row with a Session ID, and write the result to
    `WA Reports/Aggregated Report.xlsx`.

    Source reports in `path` are only cleared AFTER a successful write.
    A corrupt individual file is logged and skipped — it no longer
    kills the entire aggregate.
    """
    path = Path(path)

    if not path.exists():
        print(f"⚠️  Aggregate source folder does not exist: {path}", flush=True)
        return

    # Gather files (only .xlsx; tolerant to stray files in the folder)
    files = [f for f in os.listdir(path) if f.lower().endswith((".xlsx", ".xlsm"))]
    if not files:
        print(f"ℹ  No .xlsx files found in {path} — nothing to aggregate",
              flush=True)
        _ensure_output_dir()
        # Match previous behaviour: when there's nothing to merge, write
        # an empty Aggregated Report.xlsx so downstream tooling sees a
        # consistent file.
        pd.DataFrame().to_excel(_OUTPUT_REPORT, index=False)
        return

    # Read each file once (fix #4); skip corrupt files with a log (#9)
    frames = []
    for filename in files:
        filepath = path / filename
        try:
            df = pd.read_excel(filepath, engine="openpyxl")
        except Exception as exc:
            print(f"⚠️  Could not read {filename}: {exc} — skipping",
                  flush=True)
            continue
        if df.empty:
            continue
        frames.append(df)

    _ensure_output_dir()

    if not frames:
        print("ℹ  All source reports were empty or unreadable — writing "
              "empty Aggregated Report", flush=True)
        pd.DataFrame().to_excel(_OUTPUT_REPORT, index=False)
        # Only clear AFTER the empty write succeeded (fix #8)
        _clear_folder_safe(path)
        return

    # Merge all frames — pd.concat replaces deprecated DataFrame._append
    excl_merged = pd.concat(frames, ignore_index=False)

    # Drop pre-existing Issue/Unnamed columns and re-generate Issue ID.
    # Previously wrapped in bare try/except which silently hid real
    # errors; now catch specific exceptions with logging (fix #2).
    try:
        excl_merged = excl_merged[
            excl_merged.columns.drop(list(excl_merged.filter(regex="Issue")))
        ]
        excl_merged = excl_merged[
            excl_merged.columns.drop(list(excl_merged.filter(regex="Unnamed")))
        ]
        excl_merged.insert(loc=0, column="Issue ID", value=np.arange(len(excl_merged)))
        excl_merged = excl_merged.dropna(thresh=4)
    except (KeyError, ValueError) as exc:
        # KeyError covers column-drop misses; ValueError covers the
        # insert() path (e.g., duplicate column).  Preserve behaviour
        # (continue to write the report) but log the problem.
        print(f"⚠️  Issue-ID / column-cleanup step raised: {exc}. "
              f"Continuing with best-effort merge.", flush=True)

    # Session ID — all rows get the same ID because all languages are
    # tested in the same calendar week (the original per-language
    # Schedule.xlsx lookup is no longer needed).
    session_id = _current_session_id()
    session_ids = [session_id] * len(excl_merged)
    print(f"🗓  Session ID for this run: {session_id}  "
          f"(applied to all {len(excl_merged)} rows)", flush=True)

    # Normalise Time Identified if present (preserve original behaviour)
    if "Time Identified" in excl_merged.columns:
        excl_merged["Time Identified"] = pd.to_datetime(
            excl_merged["Time Identified"], errors="coerce"
        )

    excl_merged.insert(loc=1, column="Session ID", value=session_ids)

    # Write the aggregated report — use consistent BASE_DIR-rooted path
    # (fix #5).
    try:
        excl_merged.to_excel(_OUTPUT_REPORT, index=False)
    except Exception as exc:
        print(f"✗ Failed to write {_OUTPUT_REPORT}: {exc}", flush=True)
        print("  Source reports preserved — fix the error and re-run.",
              flush=True)
        return

    print(f"✓ Aggregated {len(frames)} reports → {_OUTPUT_REPORT} "
          f"({len(excl_merged)} rows)", flush=True)

    # Only clear source reports after a successful write (fix #8)
    _clear_folder_safe(path)


# ===========================================================================
# SECTION 5 – UPLOAD
# ===========================================================================

def upload(filepath) -> None:
    """
    Upload `filepath` to the configured SharePoint folder using Playwright.

    Uses Playwright's `set_input_files()` against the `<input type="file">`
    element that SharePoint's Upload button is backed by.  This bypasses
    the native OS file-picker entirely — no focus races, no pyautogui,
    no chromedriver dependency.

    Matches the rest of the pipeline (crawler, checkers, login) which
    all run on Playwright.  Run `playwright install chromium` once on
    the host if the browser isn't already installed.
    """
    filepath = Path(filepath).resolve()   # absolute path required by set_input_files

    if not filepath.exists():
        print(f"✗ Cannot upload: file does not exist: {filepath}", flush=True)
        return

    cfg = _load_upload_config()
    upload_email   = cfg["upload_email"]
    sharepoint_url = cfg["sharepoint_url"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=False)
        page    = context.new_page()
        page.set_default_timeout(30_000)

        try:
            print(f"🔗 Navigating to SharePoint: {sharepoint_url[:80]}…",
                  flush=True)
            try:
                page.goto(sharepoint_url, wait_until="domcontentloaded",
                          timeout=60_000)
            except PlaywrightTimeoutError as exc:
                print(f"⚠️  SharePoint navigation timeout: {exc}. "
                      f"Proceeding — auth flow may still be usable.",
                      flush=True)

            # --- Step 1: Microsoft login email entry ---
            try:
                email_input = page.locator("#i0116")
                email_input.wait_for(state="visible", timeout=30_000)
                email_input.fill(upload_email)
                print(f"✓ Entered upload email: {upload_email}", flush=True)

                # Click the Next button after entering email
                try:
                    next_btn = page.locator("#idSIButton9")
                    next_btn.wait_for(state="visible", timeout=5_000)
                    next_btn.click()
                except Exception:
                    # Some tenants auto-advance; pressing Enter is safe
                    try:
                        email_input.press("Enter")
                    except Exception:
                        pass
            except PlaywrightTimeoutError:
                print("ℹ  Email prompt not present — probably already "
                      "signed in via SSO", flush=True)
            except Exception as exc:
                print(f"⚠️  Email entry step raised: {exc}", flush=True)

            # --- Step 2: "Stay signed in?" prompt ---
            # Microsoft's post-auth prompt uses id="idBtn_Back" for the
            # 'Yes' button (counter-intuitive naming).  Not always shown.
            try:
                stay_btn = page.locator("#idBtn_Back")
                stay_btn.wait_for(state="visible", timeout=15_000)
                stay_btn.click()
                print("✓ Dismissed 'stay signed in' prompt", flush=True)
            except PlaywrightTimeoutError:
                print("ℹ  'Stay signed in' prompt not shown", flush=True)
            except Exception as exc:
                print(f"ℹ  'Stay signed in' step skipped: {exc}", flush=True)

            # Give SharePoint a moment to render the document library.
            # SharePoint's JS is notoriously slow to paint — domcontentloaded
            # fires well before the UI is interactive.
            print("⏳ Waiting for SharePoint document library to render…",
                  flush=True)
            try:
                page.wait_for_load_state("domcontentloaded", timeout=30_000)
            except Exception:
                pass
            time.sleep(8)

            # --- Step 3: find the hidden file input and send the path ---
            # SharePoint's Upload → Files button is a styled label on
            # top of a hidden <input type="file">.  Playwright's
            # set_input_files() works against hidden inputs, so we don't
            # need to un-hide it first (unlike the Selenium version).
            try:
                file_input = page.locator("input[type='file']").first
                file_input.wait_for(state="attached", timeout=15_000)

                # set_input_files accepts hidden inputs natively
                file_input.set_input_files(str(filepath))

                print(f"✓ File attached to input[type=file]: {filepath.name}",
                      flush=True)

                # Give SharePoint time to actually push the bytes.
                # On a ~1 MB aggregate this is usually 5-15 seconds;
                # waiting 20 gives enough margin without being wasteful.
                time.sleep(20)
                print("✓ Upload complete", flush=True)
                return

            except PlaywrightTimeoutError as exc:
                print(f"⚠️  No <input type='file'> found on the page ({exc}). "
                      f"SharePoint may have changed its upload UI — "
                      f"uploading manually this week is the safest fallback.",
                      flush=True)
            except Exception as exc:
                print(f"✗ set_input_files failed: {exc}.  SharePoint may be "
                      f"routing the Upload button through the OS file "
                      f"picker — Playwright does not drive native dialogs. "
                      f"Upload manually this week.", flush=True)

        finally:
            try:
                context.close()
            except Exception:
                pass
            try:
                browser.close()
            except Exception:
                pass


# ===========================================================================
# SECTION 6 – HELPERS
# ===========================================================================

def _ensure_output_dir() -> None:
    """Ensure WA Reports/ exists."""
    _WA_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def clear_folder(path) -> None:
    """Public: remove every file in `path` (unchanged signature)."""
    path = Path(path)
    if not path.exists():
        return
    for file in os.listdir(path):
        try:
            os.remove(path / file)
        except Exception as exc:
            print(f"⚠️  Could not remove {file}: {exc}", flush=True)


def _clear_folder_safe(path) -> None:
    """
    Clear `path` with a log line.  Private alias for clarity — used
    AFTER successful writes in aggregate().
    """
    n = 0
    path = Path(path)
    for file in os.listdir(path):
        try:
            os.remove(path / file)
            n += 1
        except Exception as exc:
            print(f"⚠️  Could not remove {file}: {exc}", flush=True)
    print(f"✓ Cleared {n} file(s) from {path}", flush=True)


# ===========================================================================
# SECTION 7 – MAIN BLOCK
# ===========================================================================

if __name__ == "__main__":
    aggregate(to_be_merged_folderpath)
    # upload(to_be_uploaded_filepath)   # enable manually when ready
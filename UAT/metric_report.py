import pandas as pd
import openpyxl
import threading
import time
import datetime
import functools

from pathlib import Path

BASE_DIR = Path(__file__).parent

# Create a global lock
lock = threading.Lock()

filename = str(BASE_DIR /'Metric Report/Metric_report.xlsx')
columns = {
    'Metric': ['Session ID','Demo Account', 'Country', 'Language', 'Domain', 'Start date', 'end date', 'no of links', 'Total Runtime (in mins)' ],
    'Login': ['Session ID','Demo account', 'month', 'date', 'time', 'login'],
    'Language': ['Session ID','Demo Account', 'month', 'date', 'time', 'language Changed']
}


def _week_number_of_year(date_value: datetime.date) -> int:
    """Return ISO week number of the year for a given date.

    Mirrors the yweeknumber logic from VaultSample.week_number_of_month /
    printweeknumber, but without importing that module.
    """

    return date_value.isocalendar()[1]


def _generate_metric_session_id() -> str:
    """Generate session ID in the format 'YYYY_WeekNumber'.

    This follows the same pattern as VaultSample.printweeknumber +
    merge_upload.aggregate: current calendar year + ISO week-of-year.
    """

    today = datetime.datetime.today().date()
    yweeknumber = _week_number_of_year(today)
    year = today.year
    return f"{year}_{yweeknumber}"

def metric_report(sheet_name, *args):
    if sheet_name not in columns:
        print(f"Error: Sheet '{sheet_name}' not found in defined columns.")
        return
    
    data = [args]  # Collect all arguments into a single list
    
    try:    
        df = pd.DataFrame(data, columns=columns[sheet_name])
        df_old = pd.read_excel(filename,sheet_name=sheet_name)
        df = df_old._append(df)
        # Acquire the lock
        with lock:
            with pd.ExcelWriter(filename, engine='openpyxl', mode='a',if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    except FileNotFoundError:
        print(f"Error: Excel file '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def log_module_metric(module_name):
    """Decorator to log per-module runtime into the Metric sheet.

    It does not change the wrapped function's signature. It infers
    demo account, country and language from either:
    - a bound method's `self` (expects attributes: username, country, language), or
    - the first positional argument if it is an account list/tuple
      [email, password, region, country, language, acc_type].
    """

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

                # Local session id helper (year_weekNumber), aligned with
                # VaultSample/merge_upload week-of-year usage
                session_id = _generate_metric_session_id()
                demo_account = "N/A"
                country = "N/A"
                language = "N/A"

                if args:
                    first = args[0]

                    # Case 1: bound method on an object with account attributes
                    if hasattr(first, "username"):
                        demo_account = str(getattr(first, "username", demo_account))
                        country = str(getattr(first, "country", country))
                        language = str(getattr(first, "language", language))

                    # Case 2: top-level function taking an account list/tuple
                    elif isinstance(first, (list, tuple)) and len(first) >= 5:
                        demo_account = str(first[0])
                        country = str(first[3])
                        language = str(first[4])

                try:
                    metric_report(
                        "Metric",
                        session_id,
                        demo_account,
                        country,
                        language,
                        module_name,
                        str(start_date),
                        str(end_date),
                        "",                   # no_of_links not tracked per module here
                        str(runtime_mins),
                    )
                except Exception as e:
                    print(f"Metric logging failed for module {module_name}: {e}")

        return wrapper

    return decorator


def log_login_metric(func):
    """Decorator to log login events into the Login sheet.

    It does not change the wrapped function's signature. It infers
    the demo account from either:
    - a bound method's `self` (expects attribute: username), or
    - the first positional argument if it is an account list/tuple
      [email, password, region, country, language, acc_type].
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Timestamp for this login attempt
        now = datetime.datetime.now()
        month = now.strftime("%B")
        date_str = str(now.date())
        time_str = now.strftime("%H:%M:%S")

        session_id = _generate_metric_session_id()
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
            # If the wrapped login returns a bool, use it to set status.
            if isinstance(result, bool):
                login_status = "Yes" if result else "No"
            else:
                login_status = "Yes"
            return result
        except Exception:
            login_status = "No"
            raise
        finally:
            try:
                metric_report(
                    "Login",
                    session_id,
                    demo_account,
                    month,
                    date_str,
                    time_str,
                    login_status,
                )
            except Exception as e:
                print(f"Login metric logging failed: {e}")

    return wrapper


def log_language_metric(func):
    """Decorator to log language-change events into the Language sheet.

    Assumes the wrapped method belongs to an object with attributes
    `username` and `language`, or receives an account tuple as first arg.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Timestamp
        now = datetime.datetime.now()
        month = now.strftime("%B")
        date_str = str(now.date())
        time_str = now.strftime("%H:%M:%S")

        session_id = _generate_metric_session_id()
        demo_account = "N/A"
        language_changed = "N/A"

        if args:
            first = args[0]
            if hasattr(first, "username"):
                demo_account = str(getattr(first, "username", demo_account))
            if hasattr(first, "language"):
                language_changed = str(getattr(first, "language", language_changed))
            elif isinstance(first, (list, tuple)) and len(first) >= 5:
                demo_account = str(first[0])
                language_changed = str(first[4])

        try:
            return func(*args, **kwargs)
        finally:
            try:
                metric_report(
                    "Language",
                    session_id,
                    demo_account,
                    month,
                    date_str,
                    time_str,
                    language_changed,
                )
            except Exception as e:
                print(f"Language metric logging failed: {e}")

    return wrapper

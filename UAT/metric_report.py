import pandas as pd
import openpyxl
import threading

# Create a global lock
lock = threading.Lock()

filename = 'Metric Report\\Metric_report.xlsx'
columns = {
    'Metric': ['Session ID','Demo Account', 'Domain', 'Start date', 'end date', 'no of links', 'Total Runtime (in mins)' ],
    'Login': ['Session ID','Demo account', 'month', 'date', 'time', 'login'],
    'Language': ['Session ID','Demo Account', 'month', 'date', 'time', 'language Changed']
}

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

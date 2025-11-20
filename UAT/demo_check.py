import pandas as pd
import ast
import re
from demo_attribute_check import *

file_path = r'D:\UAT\Demo_account_attribute\Demo_accounts.xlsx'
validate_path = r'D:\UAT\Demo_account_attribute\validate.xlsx'

def df_to_dict(file_path,sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Check if the values in 'Attribute' and 'UserRight' columns are strings
    df['Attribute'] = df['Attribute'].apply(lambda x: x if isinstance(x, str) else str(x))
    df['UserRight'] = df['UserRight'].apply(lambda x: x if isinstance(x, str) else str(x))

    # Apply leftstrip and rightstrip to both 'Attribute' and 'UserRight' columns
    df['Attribute'] = df['Attribute'].apply(lambda x: x.strip() if isinstance(x, str) else x)
    df['UserRight'] = df['UserRight'].apply(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Split the strings using regex
    df['Attribute'] = df['Attribute'].apply(lambda x: [str(value) for value in re.split('\n|_x000D_\n', x)])
    df['UserRight'] = df['UserRight'].apply(lambda x: [str(value) for value in re.split('\n|_x000D_\n', x)])
    
    # Convert DataFrame to dictionary
    data = df.to_dict('records')

    for row_dict in data:
        for key in row_dict:
            if isinstance(row_dict[key], list):  # Handle arrays properly
                row_dict[key] = [None if pd.isna(value) else value for value in row_dict[key]]
            else:  # For non-array values
                if pd.isna(row_dict[key]):
                    row_dict[key] = None
            
            if isinstance(row_dict[key], str) and row_dict[key].startswith('[') and row_dict[key].endswith(']'):
                try:
                    row_dict[key] = ast.literal_eval(row_dict[key])
                except Exception as e:
                    print(str(e))

    return data

# Usage
sheet_names = ['AMS','APJ','EMEA']
for sheet_name in sheet_names:

    demo_account = df_to_dict(file_path,sheet_name)

    for account in demo_account:
        while True:
            print()
            setUp()
            try:
                login(account)
                # time.sleep(10)
                process_data(account)
                generate_excel_report(account, validate_path, sheet_name)
                tearDown()
                break  # If login is successful, break out of the while loop
            except Exception as e:
                print("Login failed:", str(e))
                print("Retrying the same file...")

                

    
email(validate_path)
flag = True
if flag:
    remove_data_from_excel(validate_path)
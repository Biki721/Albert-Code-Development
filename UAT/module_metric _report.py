import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def metric_report(demo_account,start_date,end_date,no_of_links,new_tab_runtime,tvar_runtime,broken_link_runtime,trans_and_empty_runtime):
    columns = ['Demo account','Start date','End date', 'No. of links','New Tab Runtime','Tvar Runtime','Broken links Runtime', 'Translation and Empty Page Runtime']
    filename = 'Metric Report/metric_report.xlsx'  # Replace with your actual file path
    
    # If the file exists, read the existing data, otherwise create a new DataFrame
    if os.path.exists(filename):
        df = pd.read_excel(filename)
    else:
        df = pd.DataFrame(columns=columns)
    
    # Fill the DataFrame with data
    
    data = {
        'Demo account': demo_account,
        'Start date': start_date,
        'End date': end_date,
        'No. of links': no_of_links,
        'New Tab Runtime': new_tab_runtime,
        'Tvar Runtime': tvar_runtime,
        'Broken links Runtime': broken_link_runtime,
        'Translation and Empty Page Runtime': trans_and_empty_runtime,
    }
    
    df = df.append(data, ignore_index=True)
    
    # Write the DataFrame to the Excel file
    df.to_excel(filename, index=False)

metric_report()

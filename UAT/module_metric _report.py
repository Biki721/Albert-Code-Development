import pandas as pd
from datetime import datetime, timedelta
import os


def metric_report(
    demo_account,
    country,
    language,
    start_date,
    end_date,
    no_of_links,
    new_tab_runtime,
    tvar_runtime,
    broken_link_runtime,
    trans_and_empty_runtime,
    spell_runtime=None,
    external_links_runtime=None,
):
    columns = [
        'Demo account',
        'Country',
        'Language',
        'Start date',
        'End date',
        'No. of links',
        'New Tab Runtime',
        'Tvar Runtime',
        'Broken links Runtime',
        'Translation and Empty Page Runtime',
        'Spelling Runtime',
        'External Links Runtime',
    ]
    filename = 'Metric Report/metric_report.xlsx'

    # Ensure output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # If the file exists, read the existing data, otherwise create a new DataFrame
    if os.path.exists(filename):
        df = pd.read_excel(filename)
    else:
        df = pd.DataFrame(columns=columns)

    # Make sure all expected columns exist (handles older files without new columns)
    for col in columns:
        if col not in df.columns:
            df[col] = None
    df = df[columns]

    # Fill the DataFrame with data
    data = {
        'Demo account': demo_account,
        'Country': country,
        'Language': language,
        'Start date': start_date,
        'End date': end_date,
        'No. of links': no_of_links,
        'New Tab Runtime': new_tab_runtime,
        'Tvar Runtime': tvar_runtime,
        'Broken links Runtime': broken_link_runtime,
        'Translation and Empty Page Runtime': trans_and_empty_runtime,
        'Spelling Runtime': spell_runtime,
        'External Links Runtime': external_links_runtime,
    }

    df.loc[len(df)] = data

    # Write the DataFrame to the Excel file
    df.to_excel(filename, index=False)

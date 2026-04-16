import pandas as pd
import datetime

def week_number_of_month(date_value):
    """
    Calculate the week number within the month and the week number within the year for a given date.
    
    Parameters:
        date_value (datetime.date): The date for which the week numbers are calculated.
    
    Returns:
        tuple: (week number of the month, ISO week number of the year)
    """
    iso_week_of_date = date_value.isocalendar()[1]
    iso_week_of_month_start = date_value.replace(day=1).isocalendar()[1]
    week_of_month = iso_week_of_date - iso_week_of_month_start + 1
    return week_of_month, iso_week_of_date

def generate_single_session_id():
    """
    Generate a single session ID for the current week of the year.
    
    Returns:
        str: The generated session ID in the format 'YYYY_WeekNumber'.
    """
    today = datetime.datetime.today().date()
    _, yweeknumber = week_number_of_month(today)
    year = today.year
    session_id = f"{year}_{yweeknumber}"
    return session_id

# Read the languages from the Excel file
# try:
#     dff = pd.read_excel("Schedule.xlsx")
#     lang = list(dff['Language'])
# except FileNotFoundError:
#     print("Error: 'Schedule.xlsx' file not found.")
#     lang = []

# Generate a single session ID
# session_id = generate_single_session_id()
# print(session_id)

    

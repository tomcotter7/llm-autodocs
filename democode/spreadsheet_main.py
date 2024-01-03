from datetime import datetime
from .helper import day_to_column

def get_cell():
    """
    Fetches the cell reference in an Excel-like spreadsheet for today's date at a specific row.
    
    Returns:
        str: The cell reference combining the current year, month, column equivalent of today's day, and the fixed row number 38.
    """
    date = datetime.today()
    year = date.year
    month = date.strftime("%B")
    day = date.day
    sheet = str(year) + month + '!'
    column = day_to_column(day)
    return sheet+column+"38"

if __name__ == "__main__":
    print(get_cell())
from datetime import datetime
from .helper import day_to_column as dtc

def get_cell():
    """Generates a cell reference for a specific date in a spreadsheet.

    This function retrieves the current date, and formats it into a string to be used as a cell reference in a spreadsheet. The cell reference is made up of the current year, month, and day.
    Returns:
        str: A string representing the cell reference in the format 'YearMonth!Day38'
    Example:
        get_cell() # Returns: '2022July!738'
    """
    """Generates the cell location in a Google Spreadsheet based on the current date

    The function generates the cell location in Google Spreadsheet based on the current date. It first fetches the current date, extracts the year, month, and day, generates the sheet name as year concatenated with month, and finally outputs a string representing the cell which includes the sheet, column derived from day, and a static row 38.
    Returns:
        String denoting the cell in Google Spreadsheet
    Example:
        get_cell()
    """
    """Generates a cell reference for a specific date in a spreadsheet.

    This function retrieves the current date, and formats it into a string to be used as a cell reference in a spreadsheet. The cell reference is made up of the current year, month, and day.
    Returns:
        str: A string representing the cell reference in the format 'YearMonth!Day38'
    Example:
        get_cell() # Returns: '2022July!738'
    """
    date = datetime.today()
    year = date.year
    month = date.strftime("%B")
    day = date.day
    sheet = str(year) + month + '!'
    column = dtc(day)
    return sheet+column+"38"

if __name__ == "__main__":
    print(get_cell())

"""This module contains a function relevant to creating a spreadsheet cell reference based on the current date.

The main function in this module is 'get_cell', which generates a cell reference based on the current date. The function makes it easy and intuitive to extract certain elements of a spreadsheet based on the cell's date value.
"""

from datetime import datetime
from .helper import day_to_column as dtc

def get_cell():
    """Generates a cell reference based on the current date

    This function retrieves the current date and formats it to generate a cell reference in a specific format. It first gets the current date and extracts the year, month, and day. The month is transformed to its string representation. A Google Sheets style cell reference is created by combining the year, month and the string '!', then appending a specific column determined based on the day and a constant row number '38'.
    Returns:
        str
    Example:
        get_cell() # Returns '2022June!A38' if the current date is June 1, 2022
    """
    date = datetime.today()
    year = date.year
    month = date.strftime("%B")
    day = date.day
    sheet = str(year) + month + '!'
    column = dtc(day)
    return sheet+column+"38"

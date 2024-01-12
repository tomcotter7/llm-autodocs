from datetime import datetime
from .helper import day_to_column

def get_cell():
    """Generates a string representing an excel cell from today's date

    This function initially fetches the current date using datetime.today(). It subsequently extracts the year, month, and day. The month name is fetched in %B format (i.e., full month name). The day is converted into an excel column via a helper function - day_to_column. Finally, all these values are concatenated to form and return an excel cell string.

    Returns:
        string
    Example:
        get_cell() # '2022January!A38'
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

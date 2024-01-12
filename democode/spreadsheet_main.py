from datetime import datetime
from .helper import day_to_column

def get_cell():
 """Retrieve cell reference based on current date

 This function generates a cell reference in a Google sheet, based on the current date. It derives the sheet from the current year and month, and the column from the current day. Cell row is fixed to 38.

 Returns:
  string
 Example:
  get_cell() -> '2022February!D38'
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

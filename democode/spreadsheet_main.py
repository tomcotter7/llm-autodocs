from datetime import datetime
from .helper import day_to_column

def get_cell():
    date = datetime.today()
    year = date.year
    month = date.strftime("%B")
    day = date.day
    sheet = str(year) + month + '!'
    column = day_to_column(day)
    return sheet+column+"38"

if __name__ == "__main__":
    print(get_cell())
FR_MONTHS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
DATE_FORMAT = "%d-%m-%Y %H:%M:%S"


def month_number_to_french_name(month_number):
    return FR_MONTHS[month_number - 1]

def thousand_separator(value):
    try:
        value = int(value)
        return f'{value:,}'
    except:
        return value

def date_format(date):
    from datetime import datetime
    try:
        if type(date) == str:
            return datetime.strptime(date, DATE_FORMAT)
        return date.strftime(DATE_FORMAT)
    except:
        return date
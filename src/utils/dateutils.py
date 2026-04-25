import datetime

HEC_RAS_DATE_FORMAT_MS="%d%b%Y %H:%M:%S:%f" # Hour Minute Second Millisseconds
HEC_RAS_DATE_FORMAT_S="%d%b%Y %H:%M:%S" # Hour Minute Second Millisseconds
HEC_RAS_DATE_FORMAT_HM="%d%b%Y %H:%M" # Hour Minute 


def hec_ras_format_date(dt: datetime.datetime, mode: str='ms', sep: str=" ") -> str:
    """Formats datetime objects to standard HEC-RAS format.

    Args:
        dt (datetime.datetime): Datetime object to format.
        mode (str, optional): Precision mode of time. Defaults to 'ms'.
        sep (str, optional): Separator bewteen date and time. Defaults to " ".

    Returns:
        str: Formatted HEC-RAS standard datetime string.
    """
    date_format = None
    dt = round_to_5min(dt=dt)
    match mode:
        case 'ms':
            date_format = dt.strftime(HEC_RAS_DATE_FORMAT_MS)
        case 's':
            date_format = dt.strftime(HEC_RAS_DATE_FORMAT_S)
        case 'hm':
            date_format = dt.strftime(HEC_RAS_DATE_FORMAT_HM)
        case _:
            raise(ValueError(f"\"{mode}\" is not a valid formatting mode!"))

    return sep.join(date_format.lower().split(" "))

def round_to_5min(dt):

    seconds = (dt - dt.min).seconds

    rounding = (seconds + 150) // 300 * 300
    return dt + datetime.timedelta(0, rounding - seconds, -dt.microsecond)
    
if __name__ == "__main__":
    now = datetime.datetime.now()
    
    print(hec_ras_format_date(now, mode='hm', sep=','))
    
    print(round_to_5min(now))
    
from datetime import datetime

def get_time():
    now = datetime.now()
    day_month = now.strftime("%d-%m")
    hour_minute = now.strftime("%H:%M")
    return day_month, hour_minute
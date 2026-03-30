import pytz
from datetime import datetime
from pytz import timezone

TIMEZONE = 'America/Sao_Paulo'


def get_current_time():
    return datetime.now(timezone(TIMEZONE))


def parse_datetime(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00')).astimezone(pytz.utc)
        saopaulo_tz = timezone(TIMEZONE)
        return dt.astimezone(saopaulo_tz)
    except ValueError:
        raise ValueError(f"Formato de data inválido: {dt_str}")
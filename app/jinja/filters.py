import re
from datetime import datetime
from app.localization import t, timezone
from humanize import naturaltime, precisedelta


def time_fmt(value: datetime, format: str = "%H:%M"):
    return value.astimezone(timezone).time().strftime(format)


def time_ago(value: datetime):
    return naturaltime(value.astimezone(timezone), when=datetime.now(tz=timezone))

def time_delta(value):
    #val = value.replace(tzinfo=None)
    return precisedelta(value, minimum_unit="minutes", format="%0.f")


def zone_icon(value: str):
    mapping = dict(yes="⚡️", no="◼️", maybe="◻️")
    return mapping[value]

def zone_name(value: str):
    mapping = dict(yes="bot.white_zone", no="bot.black_zone", maybe="bot.gray_zone")
    return t(mapping[value])

def now_in_zone_text(value: str):
    mapping = dict(ON="bot.now_in_white_zone", OFF="bot.now_in_black_zone", UNKNOWN="bot.now_in_gray_zone")
    return t(mapping[value])

def tg_escape(value: str):
    return re.sub(r'[_*[\]()~>#\+\-=|{}.!]', lambda x: '\\' + x.group(), value)

def get_all_filters():
    return dict(time_fmt=time_fmt,
                time_ago=time_ago,
                time_delta=time_delta,
                zone_icon=zone_icon,
                zone_name=zone_name,
                now_in_zone_text=now_in_zone_text,
                tg_escape=tg_escape,
                t=t)

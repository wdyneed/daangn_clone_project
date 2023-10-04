from django import template
from django.utils.timesince import timesince
from datetime import datetime, timezone

register = template.Library()

@register.filter
def custom_timesince(value):
    now = datetime.now(timezone.utc)
    delta = now - value

    if delta.days != 0:
        return value.strftime("%Y-%m-%d")
    else:
        message_time = value.astimezone()
        now_time = now.astimezone()
        year = message_time.year
        month = str(message_time.month).zfill(2)
        day = str(message_time.day).zfill(2)
        hours = str(message_time.hour).zfill(2)
        minutes = str(message_time.minute).zfill(2)
        
        if (
            now_time.year == year and
            now_time.month == message_time.month and
            now_time.day == message_time.day
        ):
            period = '오후' if message_time.hour >= 12 else '오전'
            formatted_hours = message_time.hour % 12 or 12
            return f"{period} {formatted_hours}:{minutes}"
        else:
            return f"{year}-{month}-{day}"

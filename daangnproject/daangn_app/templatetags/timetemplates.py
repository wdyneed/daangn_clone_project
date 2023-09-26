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
    elif delta.seconds == 0:
        return "now"
    elif delta.seconds < 60:
        return f"{delta.seconds}초 전"
    elif delta.seconds // 60 < 60:
        count = delta.seconds // 60
        return f"{count}분 전"
    else:
        count = delta.seconds // 60 // 60
        return f"{count}시간 전"

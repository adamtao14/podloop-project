from datetime import datetime
from gettext import ngettext
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.timesince import timesince as django_timesince
from django.utils.timezone import now

register = template.Library()

@register.filter
@stringfilter
def seconds_to_minutes(seconds):
    minutes = int(seconds) // 60
    remaining_seconds = int(seconds) % 60
    if remaining_seconds == 0:
        return f"{minutes} min"
    else:
        return f"{minutes} min {remaining_seconds} sec"

@register.filter
def timesince_without_minutes(value):
    if value is None:
        return ''

    try:
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')

        return django_timesince(value, now()).split(', ')[0].replace(("minute"), "").strip()
    except (ValueError, TypeError):
        return ''

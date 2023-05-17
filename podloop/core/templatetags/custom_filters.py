from django import template
from django.template.defaultfilters import stringfilter

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


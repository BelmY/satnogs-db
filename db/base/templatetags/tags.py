from django import template
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def active(request, urls):
    if request.path in (reverse(url) for url in urls.split()):
        return 'active'
    return None


@register.filter
def frq(value):
    try:
        to_format = float(value)
    except (TypeError, ValueError):
        return ''
    if to_format < 1000:
        # Frequency is in Hz range
        formatted = int(to_format)
        response = format_html('{0} Hz', formatted)
    if 1000 <= to_format < 1000000:
        # Frequency is in kHz range
        formatted = format(to_format / 1000, '.3f')
        response = format_html('{0} kHz', formatted)
    if 1000000 <= to_format:
        # Frequency is in MHz range
        prec = int(to_format % 1000)
        formatted = format((to_format // 1000) / 1000, '.3f')
        if prec:
            stripped = str(prec).rstrip('0')
            formatted = format_html('{0}<small>{1}</small>', formatted, stripped)
        response = format_html('{0} MHz', formatted)
    return response

from django import template
register = template.Library()

from liliumpharm.utils import month_number_to_french_name

from rapports.models import Visite

from django.utils.safestring import mark_safe


@register.filter
def thousand_separator(value):
    try:
        value = int(value)
        return f'{value:,}'
    except:
        return value

@register.filter
def month_to_french_name(value):
    return month_number_to_french_name(value)

@register.filter
def equals(value1, value2):
    try:
        return str(value1) == str(value2)
    except:
        return False

@register.filter
def upper(value):
    try:
        return value.upper()
    except:
        return value

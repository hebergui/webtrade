import json
import statistics

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
@stringfilter
def split(value, arg):
    return value.split(arg)

@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj))

@register.filter
def get_attr(obj, attr):
    return getattr(obj, attr)

@register.filter
def get_sum(list):
    return sum(list)

@register.filter
def get_min(list):
    return min(list)

@register.filter
def get_median(list):
    return statistics.median(list)

@register.filter
def get_mean(list):
    return statistics.mean(list)

@register.filter
def get_max(list):
    return max(list)

@register.filter
def get_abs(a):
    return abs(a)
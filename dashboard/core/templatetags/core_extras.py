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
def get_sum(li):
    return sum(li)


@register.filter
def get_min(li):
    return min(li)


@register.filter
def get_median(li):
    return statistics.median(li)


@register.filter
def get_mean(li):
    return statistics.mean(li)


@register.filter
def get_max(li):
    return max(li)


@register.filter
def get_abs(a):
    return abs(a)


@register.filter
def index(indexable, i):
    if indexable is not None:
        return indexable[i]

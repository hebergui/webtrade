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

@register.filter
def antepenultimate(qs, attr):
    obj = None
    if qs.count() >= 2:
        obj = qs.order_by('-id')[1]
    else:
        return None

    if attr:
        return getattr(obj, attr)
    else:
        return obj


@register.filter
def ultimate(qs, attr):
    obj = None
    if qs.count() >= 1:
        obj = qs.order_by('-id')[0]
    else:
        return None

    if attr:
        return getattr(obj, attr)
    else:
        return obj

@register.filter
def weinstein(qs):
    obj = None
    attr = "phase"

    if qs.count() < 2:
        return ""

    indicators = qs.order_by('-id')
    pnow = indicators[0].phase[0]
    pbefore = indicators[1].phase[0]
    if pnow not in ['1', '2', '3', '4'] or pbefore not in ['1', '2', '3', '4']:
        return "N/A"

    # phase 1 -> phase 2 : buy sig
    if pbefore == '1'and pnow == '2':
        return "Buy"
    # phase 3 -> phase 4 : sell sig
    if pbefore == '3' and pnow == '4':
        return "Sell"
    # phase x -> phase x : nb
    count = indicators.count()
    if pnow == pbefore:
        i = 2
        while indicators[i].phase[0] == pnow and i < count-1:
            i += 1
        return f'{i} weeks'

    return "wait"

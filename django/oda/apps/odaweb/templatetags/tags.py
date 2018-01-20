from django import template
from django.core.serializers import serialize
from django.utils.deprecation import CallableBool
import json
from django.db.models.query import QuerySet

register = template.Library()

@register.simple_tag
def active(request, pattern, active_str="active"):
    import re
    if re.search(pattern, request.path):
        return active_str
    return ''


@register.simple_tag
def sectioncolor(flags, level):
    import colorsys

    # fix the color hue for now
    level = 30

    # if this is a code section, color it blue
    if 'SEC_CODE' in [f.name for f in flags]:
        (r,g,b) = colorsys.hsv_to_rgb(214.0/360.0, 100.0/100.0, (100.0-(1*level))/100.0)
    # else, non-code sections are different hues of black
    else:
        (r,g,b) = colorsys.hsv_to_rgb(0, 0, (10.0-(10*level))/100.0)

    return '#%02x%02x%02x' % (r*255,g*255,b*255)


def jsonify(object):
    if isinstance(object, QuerySet):
        return serialize('json', object)
    elif isinstance(object, CallableBool):
        return json.dumps(object())
    return json.dumps(object)

register.filter('jsonify', jsonify)

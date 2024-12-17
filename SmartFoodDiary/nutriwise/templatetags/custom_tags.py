import json
from django import template

register = template.Library()

@register.filter
def json(value):
    return json.dumps(value)

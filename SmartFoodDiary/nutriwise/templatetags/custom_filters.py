# nutriwise/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def replace_underscore(value, replacement):
    """Replaces underscores with the given replacement (e.g., space)."""
    return value.replace("_", replacement)
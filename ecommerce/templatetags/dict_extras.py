# templatetags/dict_extras.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get dictionary item by key
    Usage: {{ dict|get_item:key }}
    """
    return dictionary.get(key)

@register.filter
def get_item_safe(dictionary, key):
    """
    Template filter to get dictionary item by key with empty list fallback
    Usage: {{ dict|get_item_safe:key }}
    """
    if dictionary and key:
        return dictionary.get(key, [])
    return []
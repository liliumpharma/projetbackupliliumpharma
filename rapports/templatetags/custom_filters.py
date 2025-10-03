# yourapp/templatetags/custom_filters.py
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Retrieve an item from a dictionary using a key."""
    return dictionary.get(key, "")


@register.filter
def get(dictionary, key):
    """Renvoie la valeur de la clé dans le dictionnaire ou None si la clé n'existe pas."""
    return dictionary.get(key, None)  # Retourne None si la clé n'existe pas

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Retourne l'élément correspondant à la clé dans le dictionnaire."""
    return dictionary.get(key)

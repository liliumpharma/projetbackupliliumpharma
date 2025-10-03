from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Accède à une clé d'un dictionnaire dans le template"""
    return dictionary.get(key, 0)  # Retourne 0 si la clé n'existe pas

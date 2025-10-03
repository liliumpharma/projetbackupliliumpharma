from django import template

register = template.Library()


@register.filter(name="to")
def custom_to(value, arg):
    # Logique de ton filtre personnalisé
    return value  # Ou toute autre modification de la valeur

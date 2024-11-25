from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
    

@register.filter
def get_item(dictionary, key):
    """Recibe un diccionario y una clave y devuelve el valor asociado"""
    return dictionary.get(key)

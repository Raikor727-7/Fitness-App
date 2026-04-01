from django import template

register = template.Library()

@register.filter
def get_item(lst, index):
    """
    Retorna o item de uma lista pelo índice
    Uso: {{ lista|get_item:indice }}
    """
    try:
        if lst is None:
            return None
        index = int(index)
        if 0 <= index < len(lst):
            return lst[index]
        return None
    except (IndexError, ValueError, TypeError):
        return None
from django import template

register = template.Library()

@register.filter
def human_readable_number(value):
    """Sayıları insanca okunabilir formata çevirir (1000 -> 1K, 1000000 -> 1M)"""
    try:
        value = int(value)
        if value >= 1000000:
            return f"{value/1000000:.1f}M"
        elif value >= 1000:
            return f"{value/1000:.1f}K"
        else:
            return str(value)
    except (ValueError, TypeError):
        return value

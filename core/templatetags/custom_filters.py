from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    return value - arg

@register.filter(name='multiply_by')
def multiply_by(value, arg):
    return int(value) * arg

@register.filter
def calculate_aos_delay(index, base=300, increment=100):
    """Calculates the delay for AOS animation based on the index."""
    return base + index * increment
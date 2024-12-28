from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    return value - arg

@register.filter(name='multiply_by')
def multiply_by(value, arg):
    return int(value) * arg
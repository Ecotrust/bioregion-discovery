from django import template

register = template.Library()

@register.filter
def percentage(decimal, precision):
    format_string = "." + str(precision) + "%"
    return format(decimal, format_string)

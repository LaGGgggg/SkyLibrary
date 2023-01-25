from django import template

register = template.Library()


@register.filter
def to_range(number: str) -> range:
    return range(int(number))

import base64
from django import template

register = template.Library()

@register.filter(name='b64encode')
def b64encode(value):
    if value is not None:
        return base64.b64encode(value).decode('utf-8')
    return ''

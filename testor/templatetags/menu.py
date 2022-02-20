from django import template
from ..models import Topic


register = template.Library()


@register.inclusion_tag('testor/menu.html')
def show_menu():
    return {'topics': Topic.objects.all()}
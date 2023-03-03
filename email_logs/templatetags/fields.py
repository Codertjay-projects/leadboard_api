from django import template
from django.template.defaultfilters import stringfilter
import markdown as md
import requests

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name='first_word')
def first_word(words):
    return words.split().pop(0)


@register.filter(name='key_parameter')
def key_parameter(parm):
    if parm:
        return parm


@register.filter(name='count')
def count(user_action, user):
    action = user_action.filter(username=user).count()
    return action


@register.filter(name='markdown')
@stringfilter
def markdown_format(value):
    return md.markdown(value, extensions=['markdown.extensions.fenced_code'])

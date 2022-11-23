import uuid

from django.utils.text import slugify
from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    """Adding my custom pagination"""
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })
def create_slug(instance, instances, new_slug=None):
    """
    This creates a slug base on the instance provided and also if the slug exists it appends the id
    """
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = instances.objects.filter(slug=slug).order_by('-id')
    if qs.exists():
        new_slug = f'{slug}-{qs.first().id}'
        return create_slug(instance, instances, new_slug=new_slug)
    return slug

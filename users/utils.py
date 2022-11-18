import uuid

from django.utils.text import slugify


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

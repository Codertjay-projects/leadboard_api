from django.utils import timezone
from django.utils.text import slugify
import uuid


def is_valid_uuid(uuid_str):
    # Turn uuid string in to <class 'uuid.UUID'>
    # UUIDs are expected to be in the format of 8-4-4-4-12 characters separated by dashes, 
    # where each character is a hexadecimal digit (0-9, a-f).
    if uuid_str:
        try:
            return uuid.UUID(uuid_str, version=4)
        except ValueError:
            return False
    else:
        return False


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


def verify_or_convert_to_timezone(value):
    """
    this is used to convert string format datetime to timezone format
    :param value:
    :return:
    """
    if value:
        try:
            split = value.split('-')
            value = timezone.datetime(int(split[0]), int(split[1]), int(split[2]))
            return value
        except Exception as a:
            return None
    else:
        return None


def convert_words_to_date_format(date_text):
    """
    This enables converting text or words to date format which could be
    seven_days
    one_month
    :param date_text: seven_days,one_month ,
    :return: date format
    """
    try:
        if date_text == "seven_days":
            # check if the text is seven_days we then convert it to date format of seven days ago
            value = timezone.datetime.now() - timezone.timedelta(days=7)
            return value
        elif date_text == "fourteen_days":
            # check fourteen_days we then convert it to date format
            value = timezone.datetime.now() - timezone.timedelta(days=14)
            return value
        elif date_text == "twenty_eight_days":
            # check twenty_eight_days we then convert it to date format
            value = timezone.datetime.now() - timezone.timedelta(days=28)
            return value
        elif date_text == "month":
            # check month we then convert it to date format
            value = timezone.datetime.now() - timezone.timedelta(days=30)
            return value
        elif date_text == "year":
            # check year we then convert it to date format
            value = timezone.datetime.now() - timezone.timedelta(days=366)
            return value
        elif date_text == "one_month":
            value = timezone.datetime.now() - timezone.timedelta(days=30)
            return value
        return None
    except Exception as a:
        print(a)
        return None


def date_filter_queryset(request, queryset):
    """
    This filter through the queryset provided
    :param request: The request from the class or view to access params and other  ..
    :param queryset: The queryset which has been filtered by search
    :return: new created queryset
    """
    from_date = request.query_params.get("from_date")
    to_date = request.query_params.get("to_date")
    #  The date_text value could be seven_days,one_month, one_year or more, but it must be
    # a value the function convert_words_to_date_format(date_text) above^  can convert to date format
    date_text = request.query_params.get("date_text")
    try:
        if (verify_or_convert_to_timezone(from_date)
                and verify_or_convert_to_timezone(to_date)):
            # If the from_date and the to_date was passed we then filter from both the time_range
            return queryset.filter(
                timestamp__range=[verify_or_convert_to_timezone(from_date), verify_or_convert_to_timezone(to_date)])
        if verify_or_convert_to_timezone(from_date):
            # If the from_date was passed only we filter through the time range
            return queryset.filter(
                timestamp__gte=verify_or_convert_to_timezone(from_date))
        if verify_or_convert_to_timezone(to_date):
            # If the to date was passed only we filter the date till that specific date which is less than or equal to
            return queryset.filter(
                timestamp__lte=verify_or_convert_to_timezone(to_date))
        if convert_words_to_date_format(date_text):
            # check post within seven days ago, one_month or more
            return queryset.filter(
                timestamp__gte=convert_words_to_date_format(date_text))
        return queryset
    except:
        return queryset

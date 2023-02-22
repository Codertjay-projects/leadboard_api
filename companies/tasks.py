from celery import shared_task


@shared_task
def modify_all_company_send_email_count():
    """
    this is used to modify all the company email_send_count to zero every first of the month
    :return:
    """
    from .models import Company

    for item in Company.objects.all():
        item.email_sent_count = 0
        item.save()

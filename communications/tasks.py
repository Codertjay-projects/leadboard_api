from celery import shared_task


@shared_task
def create_custom_schedule_log(custom_schedule_id):
    """
    The create_custom_schedule_log functions enables us to create log of the mail we are creating to each user
    :param custom_schedule_id: the SendCustomEmailScheduler id since we cant pass instance to task
    :return: True (Note Required)
    """
    print("<<<<<<<>>>>>>>>>CUSTOM")
    # Using this import to avoid conflict
    from .models import SendCustomEmailSchedulerLog, SendCustomEmailScheduler
    # Filter base on the ID Provided
    custom_schedule = SendCustomEmailScheduler.objects.filter(id=custom_schedule_id).first()
    if not custom_schedule:
        return True
        # Get the email lists
    email_lists = custom_schedule.get_custom_emails()
    for item in email_lists:
        send_custom_email_scheduler, created = SendCustomEmailSchedulerLog.objects.get_or_create(
            email=item,
            company=custom_schedule.company,
            send_custom_email_scheduler=custom_schedule,
        )
    return True


@shared_task
def create_group_schedule_log(group_schedule_id):
    """
    The create_group_schedule_log functions enables us to create log of the mail we are creating to each user
    :param group_schedule_id: the SendGroupsEmailScheduler id since we cant pass instance to task
    :return: True (Note Required)
    """
    # Using this import to avoid conflict
    from .models import SendGroupsEmailSchedulerLog, SendGroupsEmailScheduler
    # Filter base on the ID Provided
    group_schedule = SendGroupsEmailScheduler.objects.filter(id=group_schedule_id).first()
    if not group_schedule:
        return True
        # Get the email lists
    # The email to must be added before sending the email
    pending_mail_info = group_schedule.get_lead_emails()
    for item in pending_mail_info:
        # Try getting to send group email log if it exists before and if it doesn't
        # exist I just add extra fields
        send_group_email_log, created = SendGroupsEmailSchedulerLog.objects.get_or_create(
            email=item.get("email"),
            send_groups_email_scheduler=group_schedule,
            company=group_schedule.company,
            first_name=item.get("first_name"),
            last_name=item.get("last_name"),
        )
    return True

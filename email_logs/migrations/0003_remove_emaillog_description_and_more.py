# Generated by Django 4.0.8 on 2023-03-21 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('communications', '0007_sendemailscheduler_and_more'),
        ('email_logs', '0002_emaillog_links_clicked_emaillog_links_clicked_count_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emaillog',
            name='description',
        ),
        migrations.RemoveField(
            model_name='emaillog',
            name='email_from',
        ),
        migrations.RemoveField(
            model_name='emaillog',
            name='email_subject',
        ),
        migrations.RemoveField(
            model_name='emaillog',
            name='message_id',
        ),
        migrations.RemoveField(
            model_name='emaillog',
            name='reply_to',
        ),
        migrations.RemoveField(
            model_name='emaillog',
            name='scheduled_date',
        ),
        migrations.AddField(
            model_name='emaillog',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='email_to_instance_id',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='scheduler',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scheduler_instance', to='communications.sendemailscheduler'),
        ),
        migrations.AlterField(
            model_name='emaillog',
            name='email_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='email_to_instance', to='contenttypes.contenttype'),
        ),
    ]
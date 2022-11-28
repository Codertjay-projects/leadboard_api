# Generated by Django 4.0.8 on 2022-11-28 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
        ('communications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sendgroupsemailschedulerlog',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
        migrations.AddField(
            model_name='sendgroupsemailschedulerlog',
            name='send_groups_email_scheduler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='communications.sendgroupsemailscheduler'),
        ),
        migrations.AddField(
            model_name='sendgroupsemailscheduler',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
        migrations.AddField(
            model_name='sendgroupsemailscheduler',
            name='email_to',
            field=models.ManyToManyField(blank=True, to='companies.group'),
        ),
        migrations.AddField(
            model_name='sendcustomemailscheduler',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company'),
        ),
    ]

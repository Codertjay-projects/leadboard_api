# Generated by Django 4.0.8 on 2023-03-20 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_logs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emaillog',
            name='links_clicked',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='links_clicked_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='emaillog',
            name='view_count',
            field=models.IntegerField(default=0),
        ),
    ]
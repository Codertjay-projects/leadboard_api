# Generated by Django 4.0.8 on 2022-12-02 13:34

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.CharField(max_length=250)),
                ('message_type', models.CharField(choices=[('CUSTOM', 'CUSTOM'), ('GROUP', 'GROUP'), ('HIGHVALUECONTENT', 'HIGHVALUECONTENT'), ('CAREER', 'CAREER'), ('EVENT', 'EVENT'), ('OTHERS', 'OTHERS')], max_length=250)),
                ('email_from', models.CharField(max_length=250)),
                ('email_to', models.EmailField(max_length=254)),
                ('reply_to', models.EmailField(max_length=254)),
                ('max_retries', models.IntegerField(default=0)),
                ('email_subject', models.CharField(max_length=250)),
                ('description', models.TextField()),
                ('error', models.TextField(blank=True, null=True)),
                ('scheduled_date', models.DateTimeField()),
                ('status', models.CharField(default='PENDING', max_length=50)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.company')),
            ],
        ),
    ]

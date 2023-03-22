# Generated by Django 4.0.8 on 2023-03-17 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('high_value_contents', '0003_rename_pdf_file_highvaluecontent_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='downloadhighvaluecontent',
            name='phone',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='downloadhighvaluecontent',
            name='lead_source',
            field=models.CharField(choices=[('instincthub', 'instinctHub'), ('whatsapp', 'WHATSAPP'), ('google', 'GOOGLE'), ('blog', 'BLOG'), ('facebook', 'FACEBOOK'), ('friends', 'FRIENDS'), ('webinar', 'WEBINAR'), ('news', 'NEWS'), ('others', 'OTHERS')], max_length=250),
        ),
    ]
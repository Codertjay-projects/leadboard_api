# Generated by Django 4.0.8 on 2023-02-07 21:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0004_companyemployee_invited_alter_companyemployee_role'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='headquater',
            new_name='headquarter',
        ),
    ]

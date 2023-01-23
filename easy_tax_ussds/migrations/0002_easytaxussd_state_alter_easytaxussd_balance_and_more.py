# Generated by Django 4.0.5 on 2023-01-21 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('easy_tax_ussds', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='easytaxussd',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='easy_tax_ussds.easytaxussdstate'),
        ),
        migrations.AlterField(
            model_name='easytaxussd',
            name='balance',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True),
        ),
        migrations.AlterField(
            model_name='easytaxussd',
            name='full_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='easytaxussd',
            name='lga',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='easy_tax_ussds.easytaxussdlga'),
        ),
    ]
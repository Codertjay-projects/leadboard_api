# Generated by Django 4.0.8 on 2023-03-17 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careers', '0008_alter_job_job_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='job_category',
            field=models.CharField(choices=[('instructor', 'Instructor'), ('software_dev', 'Software Development'), ('web_dev', 'Web Development'), ('mobile_dev', 'Mobile Development'), ('data_science', 'Data Science'), ('machine_learning', 'Machine Learning'), ('ai', 'Artificial Intelligence'), ('devops', 'DevOps'), ('cloud_computing', 'Cloud Computing'), ('frontend_dev', 'Front-End Development'), ('backend_dev', 'Back-End Development'), ('fullstack_dev', 'Full-Stack Development'), ('ui_ux_design', 'UI/UX Design'), ('product_management', 'Product Management'), ('project_management', 'Project Management'), ('marketing', 'Marketing'), ('sales', 'Sales'), ('customer_support', 'Customer Support'), ('finance', 'Finance'), ('hr', 'Human Resources'), ('content_creation', 'Content Creation'), ('copywriting', 'Copywriting'), ('editing', 'Editing'), ('proofreading', 'Proofreading')], max_length=250),
        ),
        migrations.AlterField(
            model_name='job',
            name='job_experience_level',
            field=models.CharField(choices=[('entry-level', 'Entry-level'), ('junior', 'Junior'), ('mid-level', 'Mid-level'), ('senior', 'Senior'), ('lead', 'Lead'), ('manager', 'Manager'), ('executive', 'Executive')], max_length=250),
        ),
    ]

# Generated by Django 4.2.7 on 2025-06-19 09:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0020_academicsession_statement_result_department_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statement_result',
            name='department',
        ),
    ]

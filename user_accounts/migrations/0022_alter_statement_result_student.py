# Generated by Django 4.2.7 on 2025-06-19 09:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0021_remove_statement_result_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statement_result',
            name='student',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='user_accounts.student'),
        ),
    ]

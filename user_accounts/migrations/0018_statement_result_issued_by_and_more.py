# Generated by Django 4.2.7 on 2025-06-18 16:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0017_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='statement_result',
            name='issued_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='issued_results', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='statement_result',
            name='signature_1',
            field=models.FileField(blank=True, null=True, upload_to='signatures/'),
        ),
        migrations.AddField(
            model_name='statement_result',
            name='signature_2',
            field=models.FileField(blank=True, null=True, upload_to='signatures/'),
        ),
    ]

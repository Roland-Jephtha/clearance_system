# Generated by Django 4.2.7 on 2025-05-03 23:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0006_student_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to='school_fee_receipts/')),
                ('title', models.CharField(max_length=100, null=True)),
                ('Exam_and_record_approved', models.BooleanField(default=False)),
                ('Hod_approved', models.BooleanField(default=False)),
                ('student_affair_approved', models.BooleanField(default=False)),
                ('hostel_approved', models.BooleanField(default=False)),
                ('student', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='user_accounts.student')),
            ],
        ),
    ]

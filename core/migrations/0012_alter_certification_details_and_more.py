# Generated by Django 5.1.3 on 2025-01-01 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_certification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certification',
            name='details',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='certification',
            name='subtitle',
            field=models.TextField(blank=True, default='', help_text='Source of the certification', null=True),
        ),
        migrations.AlterField(
            model_name='certification',
            name='title',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]

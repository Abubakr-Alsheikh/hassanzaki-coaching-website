# Generated by Django 5.1.3 on 2024-12-02 17:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coachingrequest',
            name='coaching_niche',
        ),
        migrations.RemoveField(
            model_name='coachingrequest',
            name='guests',
        ),
        migrations.RemoveField(
            model_name='coachingrequest',
            name='revenue_target',
        ),
        migrations.RemoveField(
            model_name='coachingrequest',
            name='roadblock',
        ),
    ]

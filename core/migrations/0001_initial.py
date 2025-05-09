# Generated by Django 5.1.3 on 2024-11-29 12:58

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CoachingRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date and Time')),
                ('details', models.TextField(blank=True, null=True, verbose_name='Details')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('email', models.EmailField(max_length=254, validators=[django.core.validators.EmailValidator()], verbose_name='Email')),
                ('phone', models.CharField(max_length=17, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')], verbose_name='Phone')),
                ('guests', models.IntegerField(default=0, verbose_name='Number of Guests')),
                ('coaching_niche', models.CharField(choices=[('life', 'Life'), ('business', 'Business'), ('dating', 'Dating'), ('health', 'Health'), ('career', 'Career'), ('other', 'Other')], max_length=10, verbose_name='Coaching Niche')),
                ('revenue_target', models.CharField(choices=[('5k-10k', '$5k - $10k / mo'), ('10k-20k', '$10k - $20k / mo'), ('20k-50k', '$20k - $50k / mo'), ('50k-100k+', '$50k - $100k+ / mo')], max_length=10, verbose_name='Revenue Target')),
                ('roadblock', models.CharField(choices=[('booking', 'Appointment Booking'), ('closing', 'Closing Sales'), ('retention', 'Client Retention'), ('time', 'Time'), ('other', 'Other')], max_length=10, verbose_name='Roadblock')),
                ('referral_source', models.CharField(choices=[('instagram', 'Instagram'), ('linkedin', 'LinkedIn'), ('twitter', 'Twitter'), ('facebook', 'Facebook'), ('other', 'Other')], max_length=10, verbose_name='Referral Source')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Coaching Request',
                'verbose_name_plural': 'Coaching Requests',
                'ordering': ['-scheduled_datetime'],
            },
        ),
    ]

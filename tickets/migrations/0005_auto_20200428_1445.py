# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2020-04-28 14:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_donation_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2020-05-21 11:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0004_auto_20200521_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post', to='forum.Thread'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-10 23:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20160810_0238'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sex',
            field=models.NullBooleanField(),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-22 12:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0034_event_supporter'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['-start_time']},
        ),
    ]

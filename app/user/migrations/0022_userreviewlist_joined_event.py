# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-17 18:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0037_auto_20170818_0323'),
        ('user', '0021_auto_20170817_0913'),
    ]

    operations = [
        migrations.AddField(
            model_name='userreviewlist',
            name='joined_event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='event.Event'),
        ),
    ]
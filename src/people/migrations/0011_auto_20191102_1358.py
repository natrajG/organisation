# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-11-02 13:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0010_auto_20191102_0928'),
    ]

    operations = [
        migrations.AddField(
            model_name='bills',
            name='appid',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='appbill', to='people.Application'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bills',
            name='total',
            field=models.CharField(max_length=100),
        ),
    ]

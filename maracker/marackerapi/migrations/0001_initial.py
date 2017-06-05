# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-05 08:31
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MipApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('docker_name', models.CharField(max_length=200, unique=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z-]\\/[a-zA-Z-]', 'The docker image name must have the following format: <namespace>/<image-name>')])),
                ('description', models.TextField()),
                ('cpu', models.DecimalField(decimal_places=2, default=0.1, max_digits=4, validators=[django.core.validators.MinValueValidator(0.1)])),
                ('memory', models.IntegerField(validators=[django.core.validators.MinValueValidator(32)])),
            ],
        ),
    ]

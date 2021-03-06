# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-04 12:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('body', models.CharField(max_length=2000)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('note', models.CharField(max_length=200)),
                ('path', models.CharField(help_text='Part on top of /static/images', max_length=200, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImageLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('role', models.CharField(choices=[('G', 'gallery'), ('L', 'lead'), ('S', 'social')], max_length=1)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rest_api.Article')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rest_api.Image')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

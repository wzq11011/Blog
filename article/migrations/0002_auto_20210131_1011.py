# Generated by Django 2.2.5 on 2021-01-31 02:11

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepost',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 31, 2, 11, 51, 911972, tzinfo=utc)),
        ),
    ]
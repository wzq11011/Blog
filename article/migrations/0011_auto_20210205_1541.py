# Generated by Django 2.2.5 on 2021-02-05 07:41

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0010_auto_20210205_1030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepost',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 5, 7, 41, 1, 953461, tzinfo=utc)),
        ),
    ]

# Generated by Django 5.0.2 on 2024-02-22 16:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pointage', '0016_code_employe_editable_alter_code_employe_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='code_employe',
            name='editable',
        ),
        migrations.AlterField(
            model_name='code_employe',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 2, 22, 17, 53, 34, 988999)),
        ),
    ]

# Generated by Django 5.0.2 on 2024-02-23 14:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pointage', '0017_remove_code_employe_editable_alter_code_employe_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='station',
            name='SheetID',
            field=models.CharField(max_length=70, null=True),
        ),
        migrations.AlterField(
            model_name='code_employe',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 2, 23, 15, 30, 3, 954635)),
        ),
        migrations.AlterField(
            model_name='employe',
            name='Date_Recrutement',
            field=models.DateField(default=datetime.date(2024, 2, 23)),
        ),
    ]
# Generated by Django 5.0.2 on 2024-02-20 17:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pointage', '0009_chef_station_user_alter_chef_station_id_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='chef_station',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='chef', to=settings.AUTH_USER_MODEL),
        ),
    ]

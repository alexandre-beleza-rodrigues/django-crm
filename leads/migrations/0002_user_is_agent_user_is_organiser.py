# Generated by Django 4.2.1 on 2023-05-22 21:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_agent",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="is_organiser",
            field=models.BooleanField(default=True),
        ),
    ]

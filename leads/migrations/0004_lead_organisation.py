# Generated by Django 4.2.1 on 2023-05-22 21:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0003_alter_lead_agent"),
    ]

    operations = [
        migrations.AddField(
            model_name="lead",
            name="organisation",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="leads.userprofile",
            ),
            preserve_default=False,
        ),
    ]

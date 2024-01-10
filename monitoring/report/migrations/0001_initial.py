# Generated by Django 5.0 on 2023-12-27 01:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("live", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Reaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("time", models.IntegerField()),
                ("concentration", models.IntegerField()),
                ("negative", models.IntegerField()),
                ("neutral", models.IntegerField()),
                ("positive", models.IntegerField()),
                (
                    "lecture",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="live.lecture"
                    ),
                ),
            ],
            options={
                "db_table": "reaction",
            },
        ),
        migrations.CreateModel(
            name="Feedback",
            fields=[
                (
                    "reaction",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="report.reaction",
                    ),
                ),
                ("content", models.TextField()),
            ],
            options={
                "db_table": "feedback",
            },
        ),
    ]

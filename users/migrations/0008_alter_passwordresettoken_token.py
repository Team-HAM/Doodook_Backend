# Generated by Django 5.1.4 on 2025-05-13 11:05

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_delete_userbalance"),
    ]

    operations = [
        migrations.AlterField(
            model_name="passwordresettoken",
            name="token",
            field=models.CharField(
                default=uuid.uuid4, editable=False, max_length=36, unique=True
            ),
        ),
    ]

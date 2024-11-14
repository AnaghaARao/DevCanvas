# Generated by Django 5.0.4 on 2024-11-13 08:18

import django.utils.timezone
import sequenceDiagram.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SequenceDiagram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(max_length=100)),
                ('author', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to=sequenceDiagram.models.upload_to_author)),
                ('generated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]

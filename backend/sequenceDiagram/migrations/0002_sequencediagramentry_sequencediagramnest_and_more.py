# Generated by Django 5.0.4 on 2024-11-18 04:26

import django.db.models.deletion
import django.utils.timezone
import sequenceDiagram.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sequenceDiagram', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SequenceDiagramEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=sequenceDiagram.models.upload_to_author)),
            ],
        ),
        migrations.CreateModel(
            name='SequenceDiagramNest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(max_length=100)),
                ('author', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to=sequenceDiagram.models.upload_to_author)),
                ('generated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('dir_name', models.CharField(default='default_sequence_directory', max_length=100)),
            ],
        ),
        migrations.DeleteModel(
            name='SequenceDiagram',
        ),
        migrations.AddField(
            model_name='sequencediagramentry',
            name='sequence_diagram_nest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sequence_diagram_files', to='sequenceDiagram.sequencediagramnest'),
        ),
    ]

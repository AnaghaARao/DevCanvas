# Generated by Django 5.0.4 on 2024-11-28 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploadMate', '0005_alter_filenest_dir_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filenest',
            name='dir_name',
            field=models.CharField(default='default_directory', max_length=5000),
        ),
    ]
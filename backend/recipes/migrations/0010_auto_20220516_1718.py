# Generated by Django 2.2.16 on 2022-05-16 15:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_auto_20220516_1454'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='measure_unit',
            new_name='measurement_unit',
        ),
    ]
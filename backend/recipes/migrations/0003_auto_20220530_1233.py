# Generated by Django 2.2.16 on 2022-05-30 10:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20220530_1232'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='tex',
            new_name='text',
        ),
    ]

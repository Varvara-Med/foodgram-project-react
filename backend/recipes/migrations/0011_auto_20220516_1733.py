# Generated by Django 2.2.16 on 2022-05-16 15:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_auto_20220516_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='favoriterecipe', to='recipes.Recipe', verbose_name='Рецепт'),
            preserve_default=False,
        ),
    ]
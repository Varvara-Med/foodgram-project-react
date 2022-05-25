# Generated by Django 2.2.16 on 2022-05-16 12:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20220514_2135'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ingredientinrecipe',
            name='unique_recipe_ingredient',
        ),
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='unique_cart',
        ),
        migrations.RemoveConstraint(
            model_name='tagrecipe',
            name='unique_tagrecipe',
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredient', to='recipes.Ingredient', verbose_name='Продукт рецепта'),
        ),
    ]
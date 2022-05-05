from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, ShoppingCart,
                            Recipe, Tag, )
from users.models import User


class FavoriteSerializer(serializers.ModelSerializer):
    model = Favorite
    fields = ('id', 'user', 'recipe')


class IngredientSerializer(serializers.ModelSerializer):
    model = Ingredient
    fields = ('id', 'title', 'measure_unit')


class ShoppingCartSerializer(serializers.ModelSerializer):
    model = ShoppingCart
    fields = ('id', 'user', 'recipe')


class RecipeSerializer(serializers.ModelSerializer):
    model = Recipe
    fields = ('id', 'author', 'ingredients', 'description',
              'cooking time', 'pub_date')


class TagSerializer(serializers.ModelSerializer):
    model = Tag
    fields = '__all__'

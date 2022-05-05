from django.contrib import admin

from users.models import User
from .models import (Ingredient, Recipe, Favorite)


class UserAdmin(admin.ModelAdmin):
    """
    Параметры админ зоны пользователя.
    """
    list_display = ('username', 'email', 'id')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'
    list_filter = ('username', 'email')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'measure_unit')
    search_fields = ('name', )
    empty_value_display = '-пусто-'
    list_filter = ('title',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'count_all_in_favorite')
    list_filter = ('title', 'author', 'tags')

    def count_all_in_favorite(self, obj):
        """
        Подсчёт общего числа добавлений
        этого рецепта в избранное.
        """
        return Favorite.objects.filter(recipe=obj).count()
    count_all_in_favorite.description = 'Число добавлений в избранное.'


admin.site.register(User, UserAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)

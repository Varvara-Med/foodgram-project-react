from django.contrib import admin

from users.models import User, Subscribe
from .models import (Ingredient, Recipe, Favorite, Tag, ShoppingCart,
                     IngredientInRecipe, TagRecipe)


class UserAdmin(admin.ModelAdmin):
    """
    Параметры админ зоны пользователя.
    """
    list_display = ('username', 'email', 'id')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'
    list_filter = ('username', 'email')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('title', 'measurement_unit')
    search_fields = ('name', )
    empty_value_display = '-пусто-'
    list_filter = ('title',)


class TagRecipeInLine(admin.TabularInline):
    model = TagRecipe
    extra = 0


class IngredientInRecipeInLine(admin.TabularInline):
    model = IngredientInRecipe
    extra = 0


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


class TagAdmin(admin.ModelAdmin):
    list_display = ('title', 'color', 'slug')
    search_fields = ('title',)
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Subscribe, SubscribeAdmin)

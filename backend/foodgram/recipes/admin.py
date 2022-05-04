from django.contrib import admin

from users.models import User
from .models import (Favorite, Ingredient,
                     Recipe, Tag)


class UserAdmin(admin.ModelAdmin):
    """
    Параметры админ зоны пользователя.
    """
    list_display = ('username', 'email', 'id')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'
    list_filter = ('username', 'email')


admin.site.register(User, UserAdmin)


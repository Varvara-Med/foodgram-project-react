from djoser.serializers import UserCreateSerializer
# from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, Tag,)
from users.models import User, Subscribe


class IsSubscribed(metaclass=serializers.SerializerMetaclass):
    """
    Класс определения подписки пользователя на автора.
    """
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """
        Функция обработки параметра подписчиков.
        """
        request = self.context.get('request')
        if request.user.is_anonymos:
            return False
        if Subscribe.objects.filter(user=request.user,
                                    following__id=obj.id).exists():
            return True
        return False


class RegistrationUserSerializer(UserCreateSerializer, IsSubscribed):
    """
    Сериализатор для модели пользователя.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'is_subscribed', 'last_name', 'password')
        extra_kwargs = {'is_subscribed': {'required': False}}


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор избранных рецептов.
    """
    cooking_time = serializers.IntegerField()
    # image = Base64ImageField(max_length=None, use_url=False,)

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'title', 'measure_unit')


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'description',
                  'cooking time', 'pub_date')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class SubscribeSerializer(serializers.ModelSerializer, IsSubscribed):
    """
    Сериализатор списка подписок.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_subscribed')

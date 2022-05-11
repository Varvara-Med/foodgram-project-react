from djoser.serializers import UserCreateSerializer
# from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, Tag,
                            IngredientInRecipe, TagRecipe)
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


class FavoriteRecipes(metaclass=serializers.SerializerMetaclass):
    """
    Класс определения избранных рецептов.
    """
    is_favorite = serializers.SerializerMethodField()

    def get_is_favorite(self, obj):
        """
        Функция обработки параметра избранного.
        """
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        if Favorite.objects.filter(user=request.user,
                                   recipe__id=obj.id).exists():
            return True
        return False


class RecipesCount(metaclass=serializers.SerializerMetaclass):
    """
    Класс определения количества рецептов автора.
    """

    def get_recipes_count(self, obj):
        """
        Функция подсчёта количества рецептов автора.
        """
        return Recipe.objects.filter(author__id=obj.id).count()


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
        extra_kwargs = {'title': {'required': False},
                        'measure_unit': {'required': False}}


class RecipeSerializer(serializers.ModelSerializer, FavoriteRecipes):
    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'description',
                  'cooking_time', 'pub_date', 'image', 'tags',
                  'is_favorite')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class SubscribeSerializer(serializers.ModelSerializer, IsSubscribed,
                          RecipesCount):
    """
    Сериализатор списка подписок.
    """
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_subscribed',
                  'recipes', 'recipes_count')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели продукта в рецепте. Чтение.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    title = serializers.ReadOnlyField(source='ingredient.name')
    measure_unit = serializers.ReadOnlyField(source='ingredient.measure_unit',)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'title', 'measure_unit', 'amount')


class IngredientInRecipeSerializerPost(serializers.ModelSerializer):
    """
    Сериализатор модели продукта в рецерте. Запись.
    """
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')

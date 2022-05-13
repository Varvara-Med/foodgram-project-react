from django.forms import ValidationError
from djoser.serializers import UserCreateSerializer
# from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from recipes.models import (Favorite, Ingredient, Recipe, Tag,
                            IngredientInRecipe, TagRecipe, ShoppingCart)
from users.models import User, Subscribe


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели пользователя.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """
        Функция обработки параметра подписчиков.
        """
        request = self.context.get('request')
        return(
            Subscribe.objects.filter(
                user=request.user,
                author__id=obj.id
            ).exists()
            and request.user.is_authenticated
        )

    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password')))
        return super().create(validated_data)


class ShoppingCartFavoriteRecipes(metaclass=serializers.SerializerMetaclass):
    """
    Класс определения избранных рецептов
    и продуктов корзины.
    """
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorite(self, obj):
        """
        Функция обработки параметра избранного.
        """
        request = self.context.get('request')
        return(
            Favorite.objects.filter(user=request.user, recipe__id=obj.id).exists()
            and request.user.is_authenticated
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return(
            ShoppingCart.objects.filter(user=request.user, recipe__id=obj.id).exists()
            and request.user.is_authenticated
        )


class RecipesCount(metaclass=serializers.SerializerMetaclass):
    """
    Класс определения количества рецептов автора.
    """

    def get_recipes_count(self, obj):
        """
        Функция подсчёта количества рецептов автора.
        """
        return Recipe.objects.filter(author__id=obj.id).count()


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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        extra_kwargs = {'name': {'required': False},
                        'slug': {'required': False},}


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


class RecipeSerializer(serializers.ModelSerializer,
                       ShoppingCartFavoriteRecipes):
    """
    Сериализатор модели рецептов. Чтение.
    """
    author = UserSerializer(read_only=True, many=False)
    tags = TagSerializer(many=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'description',
                  'cooking_time', 'pub_date', 'image', 'tags',
                  'is_favorite', 'is_in_shopping_cart')


class RecipeSerializerPost(serializers.ModelSerializer,
                           ShoppingCartFavoriteRecipes):
    """
    Сериализатор модели рецептов. Запись.
    """
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = IngredientInRecipeSerializerPost(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'title', 'image', 'description',
                  'ingredients', 'is_in_shopping_cart', 'tags',
                  'cooking_time', 'is_favorite')

    def validate_ingredients(self, data):
        """
        Функция проверки продуктов в рецепте.
        """
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError('Выберите как минимум 1 ингридиент!')

    def add_ingredients_and_tags(self, ingredients, recipe, tags):
        """
        Функция добавления тегов и продуктов в рецепт.
        """
        for tag in tags:
            recipe.tags.add(tag)
            recipe.save()
        for ingredient in ingredients:
            if not IngredientInRecipe.objects.filter(
                    ingredient_id=ingredient['ingredient']['id'],
                    recipe=recipe).exists():
                ingredientinrecipe = IngredientInRecipe.objects.create(
                    ingredient_id=ingredient['ingredient']['id'],
                    recipe=recipe)
                ingredientinrecipe.amoumt = ingredient['amount']
                ingredientinrecipe.save()
            else:
                IngredientInRecipe.objects.filter(recipe=recipe).delete()
                recipe.delete()
                raise serializers.ValidationError('Продукты не могут повторяться в рецепте!')
        return recipe

    def create_recipe(self, validated_data):
        """
        Функция создания рецепта.
        """
        author = validated_data.get('author')
        tags = validated_data.pop('tags')
        title = validated_data.get('title')
        image = validated_data.get('image')
        description = validated_data.get('text')
        cooking_time = validated_data.get('cooking_time')
        ingredients = validated_data.pop('ingredientinrecipe')
        recipe = Recipe.objects.create(author=author, title=title,
                                       image=image, description=description, 
                                       cooking_time=cooking_time,)
        recipe = self.add_ingredients_and_tags(tags, ingredients, recipe)
        return recipe

    def update_recipe(self, instance, validated_data):
        """
        Функция редактирования рецепта.
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientinrecipe')
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        instance = self.add_ingredients_and_tags(tags, ingredients, instance)
        super().update(instance, validated_data)
        instance.save()
        return instance


class RecipeShortFieldSerializer(serializers.ModelSerializer):
    """
    Сериализатор короткой версии отображения модели рецептов.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class SubscribeSerializer(serializers.ModelSerializer,
                          RecipesCount):
    """
    Сериализатор списка подписок.
    """
    id = serializers.ReadOnlyField(source='author.id')
    is_subscribed = serializers.SerializerMethodField()
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_recipes(self, obj):
        """
        Функция получения рецептов автора.
        """
        recipes = Recipe.objects.filter(author=obj.author)
        serializer = RecipeShortFieldSerializer(recipes, many=True)
        return serializer.data

    def get_is_subscribed(self, obj):
        """
        Функция обработки параметра подписчиков.
        """
        request = self.context.get('request')
        return(
            Subscribe.objects.filter(
                user=request.user,
                author__id=obj.id
            ).exists()
            and request.user.is_authenticated
        )


class ShoppingCartSerializer(serializers.Serializer):
    """
    Сериализатор корзины.
    """
    id = serializers.IntegerField()
    title = serializers.CharField()
    cooking_time = serializers.IntegerField()

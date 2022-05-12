from django.forms import ValidationError
from djoser.serializers import UserCreateSerializer
# from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, Tag,
                            IngredientInRecipe, TagRecipe, ShoppingCart)
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
        return(
            Subscribe.objects.filter(
                user=request.user,
                author__id=obj.id
            ).exists()
            and request.user.is_authenticated
        )


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
        if request.user.is_anonymous:
            return False
        if Favorite.objects.filter(user=request.user,
                                   recipe__id=obj.id).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        if ShoppingCart.objects.filter(user=request.user,
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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        extra_kwargs = {'name': {'required': False},
                         'slug': {'required': False},
                         }


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
    author = RegistrationUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'description',
                  'cooking_time', 'pub_date', 'image', 'tags',
                  'is_favorite', 'is_in_shopping_cart')


class RecipeSerializerPost(serializers.ModelSerializer):
    """
    Сериализатор модели рецептов. Запись.
    """
    author = RegistrationUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = IngredientInRecipeSerializerPost(source='infredientinrecipe',
                                                   many=True)
    
    class Meta:
        model = Recipe
        fields = ('id', 'author', 'title', 'image', 'text', 'ingredients',
                  'cooking_time', 'is_favorite', 'is_in_shopping_cart', 'tags')

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
        text = validated_data.get('text')
        cooking_time = validated_data.get('cooking_time')
        ingredients = validated_data.pop('ingredientinrecipe')
        recipe = Recipe.objects.create(author=author, title=title,
                                       image=image, text=text, 
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


class SubscribeSerializer(serializers.ModelSerializer, IsSubscribed,
                          RecipesCount):
    """
    Сериализатор списка подписок.
    """
    id = serializers.ReadOnlyField(source='author.id')
    is_subscribed = serializers.SerializerMethodField()
    username = serializers.ReadOnlyField(source='author.username')
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        serializer = RecipeShortFieldSerializer(recipes, many=True)
        return serializer.data


class ShoppingCartSerializer(serializers.Serializer):
    """
    Сериализатор корзины.
    """
    id = serializers.IntegerField()
    title = serializers.CharField()
    cooking_time = serializers.IntegerField()

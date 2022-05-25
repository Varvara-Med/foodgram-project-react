from django.contrib.auth.hashers import make_password

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag, TagRecipe)
from rest_framework import serializers

from users.models import Subscribe, User


class Base64ImageField(serializers.ImageField):
    """
    Класс обработки image.
    """

    def to_internal_value(self, data):
        import base64
        import uuid

        from django.core.files.base import ContentFile

        import six

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')

            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели пользователя.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password',
                  'first_name', 'last_name', 'is_subscribed')

    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password')))
        return super().create(validated_data)

    def get_is_subscribed(self, obj):
        """
        Функция обработки параметра подписчиков.
        """
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
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
        return(
            Favorite.objects.filter(user=request.user,
                                    recipe__id=obj.id).exists()
            and request.user.is_authenticated
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return(
            ShoppingCart.objects.filter(user=request.user,
                                        recipe__id=obj.id).exists()
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
        return Recipe.objects.filter(author=obj.author).count()


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор избранных рецептов.
    """
    class Meta:
        model = Favorite
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'title', 'measurement_unit')
        extra_kwargs = {'title': {'required': False},
                        'measurement_unit': {'required': False}}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        extra_kwargs = {'title': {'required': False},
                        'slug': {'required': False},}


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели продукта в рецепте. Чтение.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipeShortSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer,
                       ShoppingCartFavoriteRecipes):
    """
    Сериализатор модели рецептов. Чтение.
    """
    author = UserSerializer(many=False)
    tags = TagSerializer(many=True)
    ingredients = IngredientInRecipeSerializer(many=True,
                                               source='recipe_ingredient')
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'description',
                  'cooking_time', 'pub_date', 'image', 'tags',
                  'is_favorite', 'is_in_shopping_cart')


class RecipeShortFieldSerializer(serializers.ModelSerializer):
    """
    Сериализатор короткой версии отображения модели рецептов.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'title', 'cooking_time', 'image')


class RecipeSerializerPost(serializers.ModelSerializer,
                           ShoppingCartFavoriteRecipes):
    """
    Сериализатор модели рецептов. Запись.
    """
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = IngredientInRecipeShortSerializer(source='recipe_ingredient',
                                                    many=True)
    image = Base64ImageField(max_length=None, use_url=False,)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'title', 'image', 'description',
                  'ingredients', 'is_in_shopping_cart', 'tags',
                  'cooking_time', 'is_favorite')

    def add_ingredients_and_tags(self, tags, ingredients, recipe):
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
                ingredientinrecipe.amount = ingredient['amount']
                ingredientinrecipe.save()
            else:
                IngredientInRecipe.objects.filter(recipe=recipe).delete()
                recipe.delete()
                raise serializers.ValidationError(
                    'Продукты не могут повторяться в рецепте!'
                    )
        return recipe

    def create(self, validated_data):
        """
        Функция создания рецепта.
        """
        author = validated_data.get('author')
        tags = validated_data.pop('tags')
        title = validated_data.get('title')
        image = validated_data.get('image')
        description = validated_data.get('description')
        cooking_time = validated_data.get('cooking_time')
        ingredients = validated_data.pop('recipe_ingredient')
        recipe = Recipe.objects.create(author=author, title=title,
                                       image=image, description=description, 
                                       cooking_time=cooking_time,)
        recipe = self.add_ingredients_and_tags(tags, ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """
        Функция редактирования рецепта.
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        instance = self.add_ingredients_and_tags(tags, ingredients, instance)
        super().update(instance, validated_data)
        instance.save()
        return instance


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор списка подписок.
    """
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    is_subscribed = serializers.SerializerMethodField()
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipe_author.count',
        read_only=True
    )

    class Meta:
        model = Subscribe
        fields = ('id', 'username', 'email', 'is_subscribed',
                  'first_name', 'last_name', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        """
        Функция обработки параметра подписчиков.
        """
        request = self.context.get('request')
        if not request:
            return True
        return(
            Subscribe.objects.filter(
                user=request.user,
                author__id=obj.id
            ).exists()
            and request.user.is_authenticated
        )

    def get_recipes(self, obj):
        """
        Функция получения количества рецептов
        автора.
        """
        request = self.context.get('request')
        if request.GET.get('recipes_limit'):
            recipes_limit = int(request.GET.get('recipes_limit'))
            queryset = Recipe.objects.filter(author__id=obj.id).order_by('id')[
                :recipes_limit]
        else:
            queryset = Recipe.objects.filter(author__id=obj.id).order_by('id')
        return RecipeShortFieldSerializer(queryset, many=True).data


class ShoppingCartSerializer(serializers.Serializer):
    """
    Сериализатор корзины.
    """
    class Meta:
        model = ShoppingCart
        fields = '__all__'


class RecipeCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'title', 'image', 'cooking_time')

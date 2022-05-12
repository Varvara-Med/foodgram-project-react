from http import HTTPStatus

# from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
# from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
# from reportlab.pdfbase import pdfmetrics
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, Tag, ShoppingCart)
from users.models import User, Subscribe
# from .filters import IngredientSearchFilter, RecipeFilters
from .serializers import (RecipeSerializerPost, RegistrationUserSerializer,
                          FavoriteSerializer, RecipeShortFieldSerializer,
                          IngredientSerializer, RecipeSerializer,
                          TagSerializer, SubscribeSerializer,
                          ShoppingCartSerializer)


class CreateUserView(UserViewSet):
    """
    Обработка модели пользователя.
    """
    queryset = User.objects.all()
    serializer_class = RegistrationUserSerializer


class SubscribeViewSet(viewsets.ModelViewSet):
    """
    Обработка модели подписок.
    """
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return get_list_or_404(User, following__user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Создание подписки.
        """
        user_id = self.kwargs.get('users_id')
        user = get_object_or_404(User, id=user_id)
        Subscribe.objects.create(
            user=request.user, following=user)
        return Response(HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        """
        Удаление подписки.
        """
        user_id = request.user.id
        author_id = self.kwargs.get('users_id')
        subscribe = get_object_or_404(
            Subscribe, user__id=user_id, following__id=author_id)
        subscribe.delete()
        return Response(HTTPStatus.NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Обработка моделей рецептов.
    """
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = RecipeSerializer
    # filter_class = RecipeFilters
    # filter_backends = [DjangoFilterBackend, ]

    def get_serializer_class(self):
        """
        Функция выбора сериализатора при разных запросах.
        """
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeSerializerPost

    def perform_create(self, serializer):
        """
        Передаём данные автора при создании рецепта.
        """
        serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Обработка модели продуктов.
    """
    queryset = Ingredient.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = IngredientSerializer
    # filter_backends = (DjangoFilterBackend, IngredientSearchFilter)
    pagination_class = None
    search_fields = ['^name', ]


class CommonShoppingCartFavoriteViewSet(viewsets.ModelViewSet):
    """
    Обработка моделей корзины и избранных рецептов.
    """
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Функция создания модели корзины или избранных рецептов.
        """
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.model.objects.create(user=self.request.user, recipe=recipe)
        return Response(status=HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        """
        Функция удаления объектов в модели корзины или избранных рецептов.
        """
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        get_object_or_404(Favorite, user=self.request.user,
                          recipe=recipe).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class ShoppingCartViewSet(CommonShoppingCartFavoriteViewSet):
    """
    Обработка модели корзины.
    """
    serializer_class = ShoppingCartSerializer
    queryset = ShoppingCart.objects.all()
    model = ShoppingCart


class FavoriteViewSet(CommonShoppingCartFavoriteViewSet):
    """
    Обработка модели избранных рецептов.
    """
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()
    model = Favorite
    http_method_names = ('post', 'delete')

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Favorite.objects.create(user=self.request.user, recipe=recipe)
        serializer = RecipeShortFieldSerializer(recipe, many=False)
        return Response(data=serializer.data, status=HTTPStatus.CREATED)

    def delete(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        get_object_or_404(
            Favorite, user=self.request.user, recipe=recipe).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Обработка моделей тегов.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    paginationa_class = None

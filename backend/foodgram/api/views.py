from http import HTTPStatus

from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
# from django_filters.rest_framework import DjangoFilterBackend
# from djoser.views import UserViewSet
# from reportlab.pdfbase import pdfmetrics
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart, Tag)
from users.models import User
# from .filters import IngredientSearchFilter, RecipeFilters
from .serializers import (FavoriteSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)

                          
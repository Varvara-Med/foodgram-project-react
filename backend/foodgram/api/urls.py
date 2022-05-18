from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (UserViewSet, IngredientViewSet, RecipeViewSet,
                    SubscribeViewSet, TagViewSet, FavoriteViewSet,
                    ShoppingCartViewSet, DownloadShoppingCartViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
     path('users/subscriptions/',
          SubscribeViewSet.as_view({'get': 'list'}), name='subscriptions'),
     re_path(
        r'users/(?P<author_id>\d+)/subscribe/',
        SubscribeViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='to_subscribe'),
     re_path(
        r'recipes/(?P<recipe_id>\d+)/favorite/',
        FavoriteViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='favorites'),
     re_path(
        r'recipes/(?P<recipe_id>\d+)/shopping_cart/',
        ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='shopping_cart'),
     path('recipes/download_shopping_cart/',
          DownloadShoppingCartViewSet.as_view(), name='download'),
     path('', include('djoser.urls')),
     path('', include(router.urls)),
     path('auth/', include('djoser.urls.authtoken')),
]

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UserViewSet, IngredientViewSet, RecipeViewSet,
                    SubscribeViewSet, TagViewSet, FavoriteViewSet,
                    ShoppingCartViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
     path('users/subscriptions/',
          SubscribeViewSet.as_view({'get': 'list'}), name='subscriptions'),
     path('users/<users_id>/subscribe/',
          SubscribeViewSet.as_view({'post': 'create', 'delete': 'delete'}),
          name='subscribe'),
     path('recipes/<recipes_id>/favorite/',
          FavoriteViewSet.as_view({'post': 'create', 'delete': 'delete'}),
          name='favorite'),
     path('recipes/<recipes_id>/shopping_cart/',
          ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'delete'}),
          name='shopping_cart'),
     path('', include('djoser.urls')),
     path('', include(router.urls)),
     path('auth/', include('djoser.urls.authtoken')),
]

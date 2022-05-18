from django_filters import rest_framework as django_filter
from recipes.models import Recipe
from users.models import User


class RecipeFilter(django_filter.FilterSet):
    """
    Настройка фильтра по тегу модели рецептов.
    """
    author = django_filter.ModelChoiceFilter(queryset=User.objects.all())
    tags = django_filter.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

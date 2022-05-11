# from colorfield.fields import ColorField
from django.db import models

from users.models import User


class Tag(models.Model):
    """
    Модель тэгов.
    """
    title = models.CharField(
        'Название',
        max_length=50,
        unique=True,
    )
    color = models.CharField(
        max_length=15,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Идентификатор тега',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.title[:15]


class Ingredient(models.Model):
    title = models.CharField(
        'Наименование',
        max_length=100,
    )
    measure_unit = models.CharField(
        'Единицы измерения',
        max_length=20,
    )

    class Meta:
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.title[:15]


class Recipe(models.Model):
    """
    Модель рецептов.
    """
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        'Название',
        max_length=200,
    )
    image = models.ImageField('Картинка',)
    description = models.TextField('Описание',)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='тэги'
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        default=0,
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title[:15]


class ShoppingCart(models.Model):
    """
    Модель корзины.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор списка',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                       name='unique_cart')]

    def __str__(self):
        return self.user.username


class Favorite(models.Model):
    """
    Модель избранных рецептов.
    """
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = [models.UniqueConstraint(fields=('user', 'recipe'),
                       name='unique_favorite')]

    def __str__(self):
        return f'{self.user} likes {self.recipe}'


class IngredientInRecipe(models.Model):
    """
    Модель продуктов в рецепте.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Продукты рецепта')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')
    amount = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество продукта')

    class Meta:
        verbose_name = 'Продукты в рецепте'
        constraints = [models.UniqueConstraint(fields=['ingredient', 'recipe'],
                       name='unique_ingredientinrecipe')]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class TagRecipe(models.Model):
    """
    Модель тегов рецепта.
    """
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Теги')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Теги рецепта'
        constraints = [models.UniqueConstraint(fields=['tag', 'recipe'],
                       name='unique_tagrecipe')]

    def __str__(self):
        return f'{self.tag} {self.recipe}'

from django.db import models

from users.models import User


class Tag(models.Model):
    title = models.CharField(
        'Название',
        max_length=50,
        unique=True,
    )
    color = models.CharField(
        'Цвет',
        max_length=10,
        unique=True,
    )
    slug = models.SlugField(
        'Слаг',
        unique=True,
    )

    class Meta:
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
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='тэги'
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        default=0,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:15]


class Shoppingcart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор списка',
    )
    recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return self.user.username


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} likes {self.recipe}'

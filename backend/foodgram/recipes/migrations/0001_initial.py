# Generated by Django 2.2.16 on 2022-05-04 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Избранное',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Наименование')),
                ('measure_unit', models.CharField(max_length=20, verbose_name='Единицы измерения')),
            ],
            options={
                'verbose_name_plural': 'Ингридиенты',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('image', models.ImageField(upload_to='', verbose_name='Картинка')),
                ('description', models.TextField(verbose_name='Описание')),
                ('cooking_time', models.IntegerField(default=0, verbose_name='Время приготовления')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
            ],
            options={
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, unique=True, verbose_name='Название')),
                ('color', models.CharField(max_length=10, unique=True, verbose_name='Цвет')),
                ('slug', models.SlugField(unique=True, verbose_name='Слаг')),
            ],
            options={
                'verbose_name_plural': 'Тэги',
            },
        ),
        migrations.CreateModel(
            name='Shoppingcart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipes', models.ManyToManyField(to='recipes.Recipe', verbose_name='Рецепты')),
            ],
            options={
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Списки покупок',
            },
        ),
    ]

from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


def validate_positive_int(value):
    if value < 0:
        raise ValidationError(
            'Число не может быть отрицательным')
    if value > 32767:
        raise ValidationError(
            'Число слишком большое')


class Tag(models.Model):
    """Модель тегов рецептов."""

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id',)

    def __str__(self):
        return self.name

    name = models.CharField(
        max_length=200,
        blank=False,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=200,
        blank=False,
        unique=True,
        verbose_name='Слаг'
    )
    color = ColorField(
        blank=False,
        unique=True,
        verbose_name='Цвет'
    )


class Ingredient(models.Model):
    """Модель ингредиентов рецептов."""

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return self.name

    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Единица измерения'
    )


class Recipe(models.Model):
    """Модель рецептов."""

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-date_create',)

    def __str__(self):
        return self.name

    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название рецепта')
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        blank=False,
        verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False,
        verbose_name='Картинка'
    )
    text = models.TextField(blank=False, verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        blank=False,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        blank=False,
        validators=[validate_positive_int],
        verbose_name='Время приготовления')
    date_create = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )


class IngredientAmount(models.Model):
    """Модель ингредиентов рецептов с количеством."""

    class Meta:
        verbose_name = 'Количество'
        verbose_name_plural = 'Количество'

    def __str__(self):
        return f'{self.ingredient} - {self.recipe}'

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


class Follow(models.Model):
    """Модель подписок пользователей на автаров."""

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]

    def __str__(self):
        return f'{self.author} - {self.user}'

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик')

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')


class Favorite(models.Model):
    """Модель избранных рецептов"""

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorite_recipe',
                             verbose_name='Пользователь')

    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorite_user',
                               verbose_name='Рецепт')


class ShoppingCart(models.Model):
    """Модель списка покупок"""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='cart_recipe',
                             verbose_name='Пользователь')

    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='cart_user',
                               verbose_name='Рецепт')

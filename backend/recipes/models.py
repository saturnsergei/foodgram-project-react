from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tags(models.Model):
    """Модель тегов рецептов."""

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
    color = models.CharField(
        max_length=7,
        blank=False,
        unique=True,
        verbose_name='Цвет'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """Модель ингредиентов рецептов."""

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

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """Модель рецептов."""

    name = models.CharField(max_length=200, blank=False)
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
        Ingredients,
        through='IngredientsAmount',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='recipes',
        blank=False,
        verbose_name='Теги'
    )
    cooking_time = models.IntegerField(blank=False)
    # todo meta


class IngredientsAmount(models.Model):
    """Модель ингредиентов рецептов с количеством."""

    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    amount = models.IntegerField()  # TODO Возможно не интеджер, возможно дроби

    class Meta:
        verbose_name = 'Количество'
        # ordering = ('id',)

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class TagsRecipe(models.Model):
    """Модель связи рецептов с тегами."""

    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class Follow(models.Model):
    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик')

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')


class Favorite(models.Model):

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorite_recipe',
                             verbose_name='Пользователь')

    recipe = models.ForeignKey(Recipes,
                               on_delete=models.CASCADE,
                               related_name='favorite_user',
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]


class ShoppingCart(models.Model):

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='cart_recipe',
                             verbose_name='Пользователь')

    recipe = models.ForeignKey(Recipes,
                               on_delete=models.CASCADE,
                               related_name='cart_user',
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_user_recipe'
            )
        ]

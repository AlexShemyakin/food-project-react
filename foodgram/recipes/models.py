from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator


from .constants import (
    MAX_LENGTH_TEXT_FIELD,
    MAX_LENGTH_COLOR,
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_USER_MODEL,
    MIN_VALUE_FIELD,
    HEX_COLOR_REGEX
)


class Tag(models.Model):
    """Tag."""
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_TEXT_FIELD,
        unique=True
    )
    slug = models.SlugField(
        'Название тега в url-строке',
        max_length=MAX_LENGTH_TEXT_FIELD,
        unique=True
    )
    color = models.CharField(
        'Цвет',
        max_length=MAX_LENGTH_COLOR,
        validators=(
            RegexValidator(
                regex=HEX_COLOR_REGEX,
                message='Цвет указывается в формате HEX'
            ),
        )
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Ingredient."""
    name = models.CharField(
        max_length=MAX_LENGTH_TEXT_FIELD,
        verbose_name='Название ингредиента',
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_TEXT_FIELD,
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='ingredient_unique_constraint'
            ),
        )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Recipe."""
    name = models.CharField(
        max_length=MAX_LENGTH_TEXT_FIELD,
        verbose_name='Название рецепта',
    )
    text = models.TextField(
        'Описание рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления в минутах',
        validators=(MinValueValidator(MIN_VALUE_FIELD),)
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='ингредиенты',
    )

    class Meta:
        ordering = ('-pub_date', 'name')
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    """Recipe-Ingredient."""
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient'
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=(MinValueValidator(MIN_VALUE_FIELD),)
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )

    class Meta:
        ordering = ('ingredient', 'amount')
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='recipe_ingredient_unique_constraint'
            ),
        )


class ShoppingCart(models.Model):
    """List of shopping."""
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shoppingcart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart_constraint'
            ),
        )

    def __Str__(self) -> str:
        return f'{self.user} - {self.recipe}'


class Favorite(models.Model):
    """Favorite."""
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
        related_name='recipe'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_constraint'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'


class Follow(models.Model):
    """Follow."""
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='follower',
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following',
    )
    sub_date = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow_constraint'
            ),
            models.CheckConstraint(
                check = models.Q(user=models.F('author')),
                name='check_follow_constraint',
            )
        )

    def __str__(self) -> str:
        return (f'{self.user} follow to {self.author}')


class User(AbstractUser):
    """User."""
    username = models.CharField(
        'Логин',
        max_length=MAX_LENGTH_USER_MODEL,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH_USER_MODEL,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH_USER_MODEL,
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=MAX_LENGTH_EMAIL,
        unique=True
    )
    password = models.CharField(
        max_length=MAX_LENGTH_USER_MODEL,
        verbose_name='password'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    class Meta:
        ordering = ('-username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return f'{self.username}'

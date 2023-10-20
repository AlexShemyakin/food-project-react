from django.contrib.auth.models import AbstractUser
from django.db import models


class Tag(models.Model):
    """Tag."""
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True
    )
    slug = models.SlugField(
        'Название тега в url-строке',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        'Цвет',
        max_length=16,
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
        max_length=200,
        verbose_name='Название ингредиента',
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Recipe."""
    name = models.CharField(
        max_length=100,
        verbose_name='Название рецепта',
    )
    text = models.TextField(
        'Описание рецепта',
        max_length=500
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления в минутах',
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
    is_favorited = models.BooleanField(
        default=False,
        verbose_name='В избранном'
    )
    is_in_shopping_cart = models.BooleanField(
        default=False,
        verbose_name='В списке покупок',
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
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
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
    favorite_recipe = models.ForeignKey(
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
                fields=('user', 'favorite_recipe'),
                name='unique_shopping_cart_constraint'
            ),
        )

    def __Str__(self) -> str:
        return f'{self.user} - {self.favorite_recipe}'


class Favorite(models.Model):
    """Favorite."""
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )
    favorite_recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
        related_name='favorite_recipe'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'favorite_recipe'),
                name='unique_user_favorite_recipe_constraint'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} - {self.favorite_recipe}'


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
        )

    def __str__(self) -> str:
        return (f'{self.user} follow to {self.author}')


class User(AbstractUser):
    """User."""
    username = models.CharField(
        'Логин',
        max_length=100,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=100,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=100,
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=100,
        unique=True
    )
    password = models.CharField(
        max_length=150,
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

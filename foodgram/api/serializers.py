import base64

from rest_framework import serializers
from rest_framework.validators import ValidationError
from djoser.serializers import (
    UserCreateSerializer,
    UserSerializer
)
from django.core.files.base import ContentFile

from .utils.functions import check_unique_data
from recipes.models import (
    Tag,
    Recipe,
    RecipeIngredient,
    Ingredient,
    User,
    ShoppingCart,
    Favorite,
    Follow
)
from recipes.constants import MIN_VALUE_FIELD_AMOUNT_COOKINGTIME


class Base64ImageField(serializers.ImageField):
    """Обработка изображения."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания/удаления модели Favorite."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, attrs):
        if self.context.get('request').method == 'POST':
            if Favorite.objects.filter(
                recipe=attrs.get('recipe'),
                user=attrs.get('user')
            ).exists():
                raise ValidationError(
                    {'error': 'Рецепт уже в избранном.'}
                )
        else:
            if not Favorite.objects.filter(
                recipe=attrs.get('recipe'),
                user=attrs.get('user')
            ).exists():
                raise ValidationError(
                    {'error': 'Рецепта нет в избранном.'}
                )
        return attrs


    def to_representation(self, instance):
        return FavoriteShoppingSerializer(
            instance,
            context=self.context
        ).data


class ShoppingCartSerizlizer(FavoriteRecipeSerializer):
    """Сериализатор создания/удаления списка покупок."""

    class Meta(FavoriteRecipeSerializer.Meta):
        model = ShoppingCart

    def validate(self, attrs):
        if self.context.get('request').method == 'POST':
            if ShoppingCart.objects.filter(
                recipe=attrs.get('recipe'),
                user=attrs.get('user')
            ).exists():
                raise ValidationError(
                    {'error': 'Рецепт уже в списке покупок.'}
                )
        else:
            if not ShoppingCart.objects.filter(
                recipe=attrs.get('recipe'),
                user=attrs.get('user')
            ).exists():
                raise ValidationError(
                    {'error': 'Рецепт уже отсутствует в списке покупок.'}
                )
        return attrs


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели favorite/shoppingcart.
    Только для чтения.
    """
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = fields


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для переопределения ингридиентов
    для cериализатора рецептов.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('amount', 'id', 'name', 'measurement_unit',)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('is_subscribed',) + UserSerializer.Meta.fields

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user != obj
            and obj.following.filter(user=user).exists()
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and obj.recipe.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and obj.shoppingcart.filter(user=user).exists()
        )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeIndregientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов для создания рецептов."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(RecipeSerializer):
    """Сериализатор для создания, обновления рецепта."""
    ingredients = RecipeIndregientCreateSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'cooking_time',
            'text',
            'tags',
            'ingredients',
            'image'
        )

    def validate_ingredients(self, data):
        if not data:
            raise ValidationError({
                'error': 'Добавьте минимум один ингредиент.'
            })
        check_unique_data(data)
        return data

    def validate_tags(self, data):
        if not data:
            raise ValidationError({
                'error': 'Добавьте минимум один тег.'
            })
        check_unique_data(data)
        return data

    def validate(self, attrs):
        if not attrs.get('cooking_time'):
            raise ValidationError({
                'error': 'Укажите время приготовления.'
            })
        if attrs.get('cooking_time') < MIN_VALUE_FIELD_AMOUNT_COOKINGTIME:
            raise ValidationError({
                'error': 'Введите значение больше 1.'
            })
        return attrs

    def create_update_recipe(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient.get('id'),
                    amount=ingredient.get('amount')
                ) for ingredient in ingredients
            ]
        )

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        instance.ingredients.clear()
        self.create_update_recipe(instance, ingredients)
        instance.tags.set(tags)
        instance.save()
        return instance

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user
        )
        self.create_update_recipe(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context=self.context
        ).data


class FavoriteShoppingSerializer(serializers.ModelSerializer):
    """
    Сериализатор полей статуса избранного и списка покупок
    после создания объектов их моделей.
    """
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = (Favorite or ShoppingCart)
        fields = ['is_favorited', 'is_in_shopping_cart']

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Favorite.objects.filter(
                user=obj.user,
                recipe=obj.recipe
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(
                user=obj.user,
                recipe=obj.recipe
            ).exists()
        )


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password'
        )


class FollowingUserSerializer(CustomUserSerializer):
    """Сериализатор для подписок с рецептами."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        model = User
        fields = (
            'recipes',
            'recipes_count'
        ) + CustomUserSerializer.Meta.fields
        read_only_fields = fields

    def get_recipes(self, obj):
        return RecipeShortSerializer(
            obj.recipes,
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FollowPresentationsSerializer(serializers.ModelSerializer):
    """Сериализатор поля статуса после создания объекта модели Follow."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Follow.objects.filter(
                user=obj.user,
                author=obj.author
            ).exists()
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор создания модели Follow."""

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, attrs):
        if attrs.get('user') == attrs.get('author'):
            raise ValidationError({
                'error': 'Нельзя подписаться на самого себя.'
            })
        if Follow.objects.filter(
            user=attrs.get('user'),
            author=attrs.get('author')
        ).exists():
            raise ValidationError({
                'error': 'Вы уже подписаны на данного автора.'
            })
        return attrs

    def to_representation(self, instance):
        return FollowPresentationsSerializer(
            instance,
            context=self.context
        ).data

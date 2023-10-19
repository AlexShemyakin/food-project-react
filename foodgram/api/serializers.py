import base64
from rest_framework import serializers
from rest_framework.validators import ValidationError
from djoser.serializers import (
    UserCreateSerializer,
    UserSerializer,
    PasswordSerializer
)
from django.db import IntegrityError
from django.core.files.base import ContentFile

from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient
from recipes.models import User, ShoppingCart, Favorite, Follow


class Base64ImageField(serializers.ImageField):
    """Обработка изображения."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class ShoppingCartSerizlizer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True
    )

    class Meta:
        model = ShoppingCart
        fields = ('id',)

    def create(self, validated_data):
        obj, created = ShoppingCart.objects.get_or_create(
            favorite_recipe=validated_data.get('id'),
            user=self.context.get('request').user
        )
        if not created:
            raise ValidationError(
                {'error': 'Рецепт уже добавлен в список покупок.'}
            )
        return obj


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True
    )

    class Meta:
        model = Favorite
        fields = ('id',)

    def create(self, validated_data):
        obj, created = Favorite.objects.get_or_create(
            favorite_recipe=validated_data.get('id'),
            user=self.context.get('request').user
        )
        if not created:
            raise ValidationError(
                {'error': 'Рецепт уже добавлен в избранное.'}
            )
        return obj


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов."""
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
            'color',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов."""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для модели favorite."""
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
    """Серил. для переопределения ингридиентов для серил. рецептов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated or user == obj:
            return False
        return user.follower.filter(author=obj).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """Серил. для чтения и удаления рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = FavoriteRecipeSerializer(read_only=True)
    is_in_shopping_cart = ShoppingCartSerizlizer(read_only=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

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
            'cooking_time'
        )


class RecipeIndregientCreateSerializer(serializers.ModelSerializer):
    """Серил. для создания ингридиентов для серил. создания рецептов."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания, обновления рецепта."""
    ingredients = RecipeIndregientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    is_favorited = FavoriteRecipeSerializer(read_only=True)
    is_in_shopping_cart = ShoppingCartSerizlizer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'name',
            'cooking_time',
            'text',
            'tags',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image'
        )

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.image = validated_data.get('image')
        ingredients = validated_data.pop('ingredients')

        instance.ingredients.clear()
        recipe_ingredients = RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient.objects(
                    recipe=instance,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount']
                ) for ingredient in ingredients
            ]
        )
        instance.ingredient.set(recipe_ingredients)
        instance.tags.set(tags)
        instance.save()
        return instance

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe, created = Recipe.objects.create(
            **validated_data,
            author=self._get_user()
        )
        if not created:
            raise ValidationError({
                'error': 'Такой рецепт уже создан'
            })
        try:
            recipe_ingredients = RecipeIngredient.objects.bulk_create(
                [
                    RecipeIngredient.objects(
                        recipe=recipe,
                        ingredient=ingredient['ingredient'],
                        amount=ingredient['amount']
                    ) for ingredient in ingredients
                ]
            )
        except IntegrityError:
            raise ValidationError({
                'error': 'Ингредиент уже добавлен'
            })
        recipe.ingredient.set(recipe_ingredients)
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


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


class SetPasswordSerializer(PasswordSerializer):
    current_password = serializers.CharField(
        required=True,
        label='Текущий пароль'
    )

    def validate(self, data):
        if data['new_password'] == data['current_password']:
            raise serializers.ValidationError({
                "new_password": "Пароли не должны совпадать"})
        return data


class FollowingUserSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок с рецептами."""
    id = serializers.IntegerField(
        read_only=True
    )
    email = serializers.CharField(
        read_only=True
    )
    username = serializers.CharField(
        read_only=True
    )
    first_name = serializers.CharField(
        read_only=True
    )
    last_name = serializers.CharField(
        read_only=True
    )
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if self.context.get('request').user.is_authenticated:
            return (
                Follow.objects.filter(
                    user=self.context.get('request').user,
                    author=obj
                ).exists()
            )

    def get_recipes(self, obj):
        recipes = obj.recipes
        limit = self.context.get('request').query_params.get('limit')
        return FollowRecipeSerializer(
            recipes,
            many=True,
            context=self.context
        ).data[:limit]

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def create_follow(self, obj):
        user = self.context.get('request').user
        return Follow.objects.create(
            user=user,
            author=obj
        )


class FollowRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для доп. полей модели подписок."""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = fields


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор модели Follow"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Follow
        fields = ('id',)

    def create(self, validated_data):
        return Follow.objects.get_or_create(
            author=validated_data.get('id'),
            user=self.context.get('request').user
        )

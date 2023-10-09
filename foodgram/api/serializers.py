from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer, PasswordSerializer
from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient
from recipes.models import User, ShoppingCart, Favorite, Follow


LIMIT = 10


class TagSerializer(serializers.ModelSerializer):
    """Серил. для тэгов."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


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


class RecipeSerializer(serializers.ModelSerializer):
    """Серил. для рецептов."""
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients'
    )

    class Meta:
        model = Recipe
        # fields = '__all__'
        fields = (
            'id',
            'name',
            'text',
            'cooking_time',
            'author',
            'tags',
            'ingredients'
        )
        
    # def get_ingredients(self, instance):
    #     return RecipeIngredientSerializer(
    #         instance.recipe_ingredients.all(),
    #         many=True
    #     ).data


class RecipeIndregientCreateSerializer(serializers.ModelSerializer):
    """Серил. для создания ингридиентов для серил. создания рецептов."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
          model = RecipeIngredient
          fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Серил. для создания рецепта."""
    ingredients = RecipeIndregientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    class Meta:
        model = Recipe
        fields = ('name', 'cooking_time', 'text', 'tags', 'ingredients')

    def update(self, instance, validated_data):

        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        ingredients = validated_data.pop('ingredients')

        for ingredient in ingredients:
            RecipeIngredient.objects.update(
                recipe=instance,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
        return super().update(instance, validated_data)


    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)

        for ingredients_data in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredients_data['ingredient'],
                amount=ingredients_data['amount']
            )
        return instance

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

class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

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
        if self.context.get('request').user.is_authenticated:
            return (
                Follow.objects.filter(
                    user=self.context.get('request').user,
                    author=obj
                ).exists()
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


class ShoppingCartSerizlizer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'cooking_time')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок с рецептами."""
    id = serializers.IntegerField(
        # source='id',
        read_only=True
    )
    email = serializers.CharField(
        # source='author.email',
        read_only=True
    )
    username = serializers.CharField(
        # source='author.username',
        read_only=True
    )
    first_name = serializers.CharField(
        # source='author.first_name',
        read_only=True
    )
    last_name = serializers.CharField(
        # source='author.last_name',
        read_only=True
    )
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count'
        )
        read_only_fields = fields

    def get_recipes(self, obj):
        recipes = obj.recipes
        return FollowRecipeSerializer(
            recipes,
            many=True,
            context=self.context
        ).data
    
    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def create_follow(self, obj):
        user = self._get_user()
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
            # 'image',
            'cooking_time'
        )
        read_only_fields = fields


class FollowUserSerializer(serializers.ModelSerializer):
    pass

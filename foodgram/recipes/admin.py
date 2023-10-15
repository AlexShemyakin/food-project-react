from django.contrib import admin

from .models import Tag, Recipe, Ingredient, RecipeIngredient
from .models import ShoppingCart, Favorite, Follow, User


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = (
        'name',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )
    list_display = (
        'id',
        'name',
        'author',
    )
    list_filter = (
        'author',
        'name',
        'tags'
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
        'color',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'favorite_recipe',
    )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'recipes_count'
    )
    list_filter = (
        'email',
        'username'
    )

    def recipes_count(self, obj):
        return obj.recipes.all().count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'favorite_recipe'
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'user',
        'sub_date'
    )

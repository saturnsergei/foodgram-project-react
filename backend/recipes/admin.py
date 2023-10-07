from django.contrib import admin

from .models import (Tag, Ingredient, Recipe, IngredientAmount,
                     Follow, ShoppingCart, Favorite)


class IngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1
    autocomplete_fields = ['ingredient']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'image',
                    'text', 'cooking_time', 'date_create',)
    readonly_fields = ('favorite_count',)
    inlines = (IngredientInline,)
    search_fields = ('name',)
    list_filter = ('tags', 'author')

    def favorite_count(self, obj):
        return obj.favorite_user.count()
    favorite_count.short_description = 'Количество добавлений в избранное'


@admin.register(IngredientAmount)
class IngredientAmount(admin.ModelAdmin):
    model = IngredientAmount
    list_display = ('id', 'ingredient', 'recipe', 'amount',)
    autocomplete_fields = ['ingredient']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    inlines = (IngredientInline,)


admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)

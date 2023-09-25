from django.contrib import admin

from .models import (Tag, Ingredient, Recipe, IngredientAmount,
                     Follow, ShoppingCart, Favorite)


class IngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'image', 
                    'text', 'cooking_time', 'date_create',)
    readonly_fields = ('favorite_count',)
    inlines = (IngredientInline,)
    search_fields = ('name',)
    list_filter = ('tags', 'author')

    def favorite_count(self, obj):
        return obj.favorite_user.count()
    favorite_count.short_description = 'Количество добавлений в избранное'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientAmount)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)

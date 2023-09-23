from django.contrib import admin

from .models import Tag, Ingredient, Recipe, IngredientAmount, Follow, ShoppingCart, Favorite


class IngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'image', 'text', 'cooking_time', 'date_create')
    inlines = (IngredientInline,)
    # search_fields = ('text',)
    # list_filter = ('pub_date',)
    # empty_value_display = '-пусто-'


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(IngredientAmount)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)

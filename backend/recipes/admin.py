from django.contrib import admin

from .models import Tags, Ingredients, Recipes, IngredientsAmount, Follow, ShoppingCart, Favorite


class IngredientsInline(admin.TabularInline):
    model = IngredientsAmount
    extra = 1


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'image', 'text', 'cooking_time', 'date_create')
    inlines = (IngredientsInline,)
    # search_fields = ('text',)
    # list_filter = ('pub_date',)
    # empty_value_display = '-пусто-'


admin.site.register(Tags)
admin.site.register(Ingredients)
admin.site.register(IngredientsAmount)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)

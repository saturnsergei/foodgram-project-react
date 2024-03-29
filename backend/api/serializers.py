import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Tag, Ingredient, Recipe,
                            IngredientAmount)

User = get_user_model()


class IsSubscribedSerializer(serializers.ModelSerializer):
    """Сериализатор вычисления подписан ли пользователь на автора."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.following.filter(user=request.user).exists()
        return False


class UserSerializer(IsSubscribedSerializer):
    """Сериализатор для модели пользователя."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password', 'is_subscribed')
        write_only_fields = ('password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"])
        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения пароля."""
    new_password = serializers.CharField(write_only=True, required=True)
    current_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('new_password', 'current_password',)

    def validate(self, data):
        user = self.instance
        if not check_password(data.get('current_password'), user.password):
            raise serializers.ValidationError(
                'Неправильный пароль')
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов"""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов"""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для количества ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class Base64ImageField(serializers.ImageField):
    """Сериализатор для обработки изображения."""
    def to_representation(self, value):
        if value:
            return value.url
        return None

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов"""

    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set', many=True, read_only=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context.get('user')
        if user.is_authenticated:
            return obj.favorite_user.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('user')
        if user.is_authenticated:
            return obj.cart_user.filter(user=user).exists()
        return False

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')
        read_only_fields = ('author',)
        depth = 1

    def create_update_ingredients(self, recipe):
        if 'ingredients' in self.initial_data:
            ingredients = self.initial_data.get('ingredients')
            amount_list = []
            for ingredient in ingredients:
                id = ingredient.get('id')
                amount = ingredient.get('amount')
                amount_item = IngredientAmount(
                    ingredient_id=int(id), recipe=recipe, amount=amount
                )
                amount_list.append(amount_item)
            IngredientAmount.objects.bulk_create(amount_list)
        else:
            raise serializers.ValidationError(
                {'ingredients': ['Обязательное поле.']})

    def create(self, validated_data):
        recipe = Recipe.objects.create(**validated_data)
        self.create_update_ingredients(recipe)
        if 'tags' in self.initial_data:
            tags = self.initial_data.get('tags')
            recipe.tags.set(tags)
        else:
            raise serializers.ValidationError(
                {'tags': ['Обязательное поле.']})
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        IngredientAmount.objects.filter(recipe=instance).delete()
        self.create_update_ingredients(instance)
        if 'tags' in self.initial_data:
            tags = self.initial_data.get('tags')
            instance.tags.set(tags)
        else:
            raise serializers.ValidationError(
                {'tags': ['Обязательное поле.']})
        instance.__dict__.update(**validated_data)
        instance.save()
        return instance


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для сокращенной модели рецептов."""
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time',
        )
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(IsSubscribedSerializer):
    """Сериализатор для подписки пользователя на автора."""

    recipes_count = serializers.SerializerMethodField()
    recipes = RecipeShortSerializer(many=True, read_only=True)

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name', 'is_subscribed', 'recipes',
                            'recipes_count')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None and recipes_limit.isdigit():
            recipes_limit = int(recipes_limit)
            data['recipes'] = data['recipes'][:recipes_limit]

        return data


class FollowSubscribeSerializer(FollowSerializer):
    """Сериализатор для валидации подписок."""

    def validate(self, data):
        author = self.instance
        request = self.context['request']
        if request.user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')
        if author.following.filter(user=request.user).exists():
            raise serializers.ValidationError('Нельзя подписаться второй раз')
        return data


class FavoriteSerializer(RecipeShortSerializer):
    """Сериализатор для валидации избранных рецептов."""

    def validate(self, data):
        recipe = self.instance
        user = self.context['user']
        if recipe.favorite_user.filter(user=user).exists():
            raise serializers.ValidationError(
                'Нельзя добавить в избранное второй раз')
        return data


class ShoppingCartSerializer(RecipeShortSerializer):
    """Сериализатор для списка покупок."""

    def validate(self, data):
        recipe = self.instance
        user = self.context['user']
        if recipe.cart_user.filter(user=user).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок')
        return data

from datetime import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import Tags


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов рецептов"""

    class Meta:
        model = Tags

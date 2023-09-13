from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from recipes.models import Tags
from .serializers import TagsSerializer


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None

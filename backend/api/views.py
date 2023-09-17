from rest_framework import filters, mixins, status, viewsets
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated


from recipes.models import Tags, Ingredients, Recipes
from .serializers import TagsSerializer, IngredientsSerializer, RecipesSerializer, TokenSerializer, UserSerializer, ChangePasswordSerializer

User = get_user_model()


class TokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, email=serializer.data.get('email'))

        refresh = RefreshToken.for_user(user)

        return Response(
            {'auth_token': str(refresh.access_token)},
            status=status.HTTP_201_CREATED)


class UserViewSet(mixins.CreateModelMixin, 
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):

    permission_classes = (AllowAny,)

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,))
    def me(self, request):

        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = ChangePasswordSerializer(instance=request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):        
            new_password = serializer.validated_data.get('new_password')
            request.user.set_password(new_password)
            request.user.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

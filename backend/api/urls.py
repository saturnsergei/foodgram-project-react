from django.urls import include, path
from rest_framework import routers

from . import views

app_name = 'api'

router_v1 = routers.DefaultRouter()
# router_v1.register(r'categories', CategoryViewSet)
# router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'tags', views.TagViewSet)
router_v1.register(r'ingredients', views.IngredientViewSet)
router_v1.register(r'recipes', views.RecipeViewSet)
router_v1.register(r'users', views.UserViewSet, basename='users')
# router_v1.register(
#     r'^titles/(?P<title_id>\d+)/reviews',
#     ReviewViewSet,
#     basename='reviews'
# )
# router_v1.register(
#     r'^titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet,
#     basename='comments'
# )
# router_v1.register('users', UserViewSet, basename='users')

auth = [
    path('token/login/', views.TokenView.as_view()),
    # path('token/logout/', views.Logout.as_view()),
]

urlpatterns = [
    path('auth/', include(auth)),
    path('', include(router_v1.urls)),
]

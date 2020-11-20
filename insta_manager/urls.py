from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'instagram', views.UserInstagramViewSet)
router.register(r'friend', views.FriendViewSet)
router.register(r'^post', views.PostViewSet)

urlpatterns = [
            path('post/user/<str:username>', views.getUserPosts),
            path('user/password/', views.changePassword),
            *router.urls]

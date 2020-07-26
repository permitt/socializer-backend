from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'instagram', views.UserInstagramViewSet)
router.register(r'follower', views.FriendViewSet)
router.register(r'^post/(?P<username>.+)/$', views.PostViewSet)

urlpatterns = router.urls

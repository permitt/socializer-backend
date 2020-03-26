from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'user', views.UserInstagramViewSet)
router.register(r'follower', views.FollowerViewSet)
router.register(r'^post/(?P<username>.+)/$', views.PostViewSet)

urlpatterns = router.urls

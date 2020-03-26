from django.shortcuts import render
from rest_framework import viewsets, permissions, serializers
from rest_framework import exceptions
from insta_manager.models import UserInstagram, Follower, Post
from .serializers import UserInstagramSerializer, FollowerSerializer, PostSerializer



# Create your views here.
class UserInstagramViewSet(viewsets.ModelViewSet):
    queryset = UserInstagram.objects.all()
    serializer_class = UserInstagramSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Provjeri postoji li vec vezan za ulogovan user, vrati gresku ako ima

        # Provjeri mozes li se ulogovat, ako ne vrati gresku odgovarajucu

        serializer.save(user=self.request.user)

class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        try:
            mainIG = self.request.user.ig
        except:
            raise exceptions.ValidationError('A user doesn\'t have an IG account.')

        return Follower.objects.filter(owner=mainIG)

    # Odje pokreces taskove za scrapovanje, pravis schedule,
    def perform_create(self, serializer):
        # Prvo provjeri ima li korisnik unesen IG
        try:
            mainIG = self.request.user.ig
        except:
            raise exceptions.ValidationError('A user doesn\'t have an IG account.')
        # Drugo odradi provjeru postoji li taj username i da li ga prati korisnik

        serializer.save(owner=mainIG)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'delete']

    def get_queryset(self):
        try:
            mainIG = self.request.user.ig
        except:
            raise serializers.ValidationError('A user doesn\'t have an IG account.')
        owner = self.kwargs['username']
        return Post.objects.filter(owner__username=owner)
    #
    def perform_create(self, serializer):
        pass
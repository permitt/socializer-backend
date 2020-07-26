from django.shortcuts import render
from rest_framework import viewsets, permissions, serializers, status
from rest_framework import exceptions
from rest_framework.response import Response

from insta_manager.models import UserInstagram, Friend, Post
from scraper.services import check_login
from .serializers import UserInstagramSerializer, FriendSerializer, PostSerializer



# Create your views here.
class UserInstagramViewSet(viewsets.ModelViewSet):
    queryset = UserInstagram.objects.all()
    serializer_class = UserInstagramSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        username, password = request.data.values()
        # Provjeri postoji li vec vezan za ulogovan user, vrati gresku ako ima
        found = UserInstagram.objects.filter(username=username).first()
        if found:
            return Response({'detail': 'That account has already been added!'}, status=status.HTTP_400_BAD_REQUEST)
        # Provjeri mozes li se ulogovat, ako ne vrati gresku odgovarajucu

        if not check_login(username, password):
            return Response({'detail': 'Can\'t login with this username and password'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid()
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FriendViewSet(viewsets.ModelViewSet):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        try:
            mainIG = self.request.user.ig
        except:
            raise exceptions.ValidationError('A user doesn\'t have an IG account.')

        return Friend.objects.filter(owner=mainIG)

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
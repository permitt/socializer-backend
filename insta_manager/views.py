from django.shortcuts import render
from django_q.models import Schedule
from django_q.tasks import schedule
from rest_framework import viewsets, permissions, serializers, status
from rest_framework import exceptions
from rest_framework.decorators import api_view
from rest_framework.response import Response

from insta_manager.models import UserInstagram, Friend, Post
from scraper.services import check_login, valid_friend, fetch_data
from socializer.views import MyTokenObtainPairView
from .serializers import UserInstagramSerializer, FriendSerializer, PostSerializer


class UserInstagramViewSet(viewsets.ModelViewSet):
    queryset = UserInstagram.objects.all()
    serializer_class = UserInstagramSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_value_regex = '[\w.@+-]+'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        username, password = request.data.values()
        # Provjeri postoji li vec vezan za ulogovan user, vrati gresku ako ima
        found = UserInstagram.objects.filter(username=username).first()
        if found:
            return Response({'detail': 'That account has already been added!'}, status=status.HTTP_400_BAD_REQUEST)
        # Provjeri mozes li se ulogovat, ako ne vrati gresku odgovarajucu

        success, picture, cookies = check_login(username, password)
        if not success:
            return Response({'detail': 'Can\'t login with this username and password'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.is_valid()
        serializer.save(user=request.user, picture=picture, cookies=cookies)
        return Response({'picture': picture, 'username': username}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

class FriendViewSet(viewsets.ModelViewSet):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        try:
            mainIG = self.request.user.instagram
        except:
            raise exceptions.ValidationError('A user doesn\'t have an IG account.')

        return Friend.objects.filter(followedBy=mainIG)

    # Odje pokreces taskove za scrapovanje, pravis schedule,
    def create(self, request, *args, **kwargs):
        username = request.data['username']
        # Prvo provjeri ima li korisnik unesen IG
        if request.user.instagram is None:
            return Response({'detail':'You must first add your account!'}, status=status.HTTP_400_BAD_REQUEST)

        if Friend.objects.filter(username=username, followedBy=request.user.instagram).first():
            return Response({'detail': 'You are already stalking this dude'}, status=status.HTTP_400_BAD_REQUEST)
        # Drugo odradi provjeru postoji li taj username i da li ga prati korisnik
        valid, data = valid_friend(request.user.instagram, username)
        if not valid:
            return Response({'detail': 'Cannot follow that friend'}, status=status.HTTP_400_BAD_REQUEST)

        emailNotification = request.data['emailNotif']
        del request.data['emailNotif']

        data = { **request.data, **data}
        data['followedBy'] = request.user.instagram
        serializer = self.get_serializer(data=data)
        serializer.is_valid()
        serializer.save()

        #fetch_data(serializer.instance.username, request.user.username, False)
        schedule('scraper.services.fetch_data', serializer.instance.username, request.user.username, emailNotification, schedule_type=Schedule.DAILY, name=serializer.instance.username)
        return Response(request.data, status=status.HTTP_201_CREATED)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        print(Schedule.objects.get(name=instance))
        Schedule.objects.get(name=instance.username).delete()
        instance.delete()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'delete']

    def get_queryset(self):
        if self.request.method == 'DELETE':
            return Post.objects.all()

        try:
            mainIG = self.request.user.ig
        except:
            raise serializers.ValidationError('A user doesn\'t have an IG account.')
        owner = self.kwargs['username']
        return Post.objects.filter(owner__username=owner)


@api_view(['GET'])
def getUserPosts(request, *args, **kwargs):
    user = request.user.instagram
    friend = Friend.objects.filter(username=kwargs['username'], followedBy=user).first()
    if not friend:
        return Response({'detail': 'You Can\'t access this page'}, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    posts = Post.objects.filter(owner=friend)
    response = PostSerializer(many=True, data=posts)
    response.is_valid()
    return Response(response.data, status=status.HTTP_200_OK, content_type='application/json')


@api_view(['PUT'])
def changePassword(request, *args, **kwargs):

    user = request.user
    newPW = request.data['password']
    if len(newPW) < 6:
        return Response({'detail': 'Password must be atleast 6 characters long.'}, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    user.set_password(newPW)
    user.save()
    return Response({'detail':'changed pw', 'msg':'Password changed'}, status=status.HTTP_200_OK)
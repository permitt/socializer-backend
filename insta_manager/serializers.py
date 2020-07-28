from rest_framework import serializers
from .models import UserInstagram, Friend, Post


class UserInstagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInstagram
        exclude = ['user', 'cookies']


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

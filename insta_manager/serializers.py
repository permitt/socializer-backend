from rest_framework import serializers
from .models import UserInstagram, Follower, Post


class UserInstagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInstagram
        exclude = ['user', 'cookies']


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = ['username','firstName','lastName','picture']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

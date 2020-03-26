from django.contrib import admin
from .models import UserInstagram, Follower, Post
# Register your models here.
admin.site.register(UserInstagram)
admin.site.register(Follower)
admin.site.register(Post)

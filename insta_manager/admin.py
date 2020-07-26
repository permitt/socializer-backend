from django.contrib import admin
from .models import UserInstagram, Friend, Post
# Register your models here.
admin.site.register(UserInstagram)
admin.site.register(Friend)
admin.site.register(Post)

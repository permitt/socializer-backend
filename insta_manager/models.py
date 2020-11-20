from pathlib import Path
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import signals
from django.db import models
# Create your models here.
from django_q.tasks import schedule


class UserInstagram(models.Model):
    user = models.OneToOneField(User, related_name='instagram', on_delete=models.CASCADE)
    username = models.CharField(max_length=50, blank=False, primary_key=True)
    password = models.CharField(max_length=50)
    picture = models.CharField(max_length=300, blank=True)
    cookies = models.TextField()
    lastActive = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Friend(models.Model):
    username = models.CharField(max_length=50, primary_key=True)
    user_id = models.IntegerField(blank=True)
    fullName = models.CharField(max_length=100, blank=True)
    picture = models.CharField(max_length=300, blank=True)

    followedBy = models.ForeignKey(UserInstagram, related_name='following', on_delete=models.CASCADE)
    activeStory = models.BooleanField(default=False)
    activePosts = models.BooleanField(default=False)
    lastPost = models.DateTimeField(auto_now_add=True)
    lastStory = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


# def follower_post_save(sender : Friend, instance, created, *args, **kwargs):
#     """
#     Function that will schedule fetching data about Follower every hour
#     :param sender: Follower class
#     :param instance: Follower instance being saved
#     :param created: Boolean, true if creating new instance
#     :return:
#     """
#     if created:
#         schedule('services.fetch_data',
#                  instance,
#                  hook='hooks.print_result',
#                  schedule_type='H',
#                  )
#
#
# signals.post_save.connect(receiver=follower_post_save, sender=Friend)


class Post(models.Model):

    class Meta:
        constraints = [models.UniqueConstraint(fields=['owner','uploadedAt'], name='unique post')]

    class PostType(models.TextChoices):
        STORY = 'STORY', ('Story')
        POST = "POST", ('Post')

    owner = models.ForeignKey(Friend, related_name='posts', on_delete=models.CASCADE)
    uploadedAt = models.DateTimeField()
    url = models.URLField()
    image = models.ImageField(upload_to='images')
    type = models.CharField(max_length=10, choices=PostType.choices, default=PostType.POST)

    # Redefined to store image post locally from URL
    # Needs fixing ImageField, to be updated
    def save(self, *args, **kwargs):
        extension = kwargs['extension']
        folder_name = kwargs['folder_name']
        img_data = requests.get(self.url).content
        Path('.' + settings.STATIC_URL + folder_name).mkdir(parents=True, exist_ok=True)
        img_name = '.' + settings.STATIC_URL + folder_name + str(self.uploadedAt).replace(':','-') + extension
        with open(img_name, "wb") as f:
            f.write(img_data)

        del kwargs['extension']
        del kwargs['folder_name']
        super(Post, self).save(*args, **kwargs)
        print("SACUVAN POST ", img_name)

    def __str__(self):
        return f'{self.owner} : {self.uploadedAt} | {self.type}'

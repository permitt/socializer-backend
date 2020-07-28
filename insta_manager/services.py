from django.core.mail import send_mail

from insta_manager.email import TITLE, BODY
from insta_manager.models import UserInstagram, Friend
from socializer import settings


def send_email(toUser: UserInstagram, friend: str):
    send_mail(TITLE.format(friend),
              BODY.format(friend),
              settings.EMAIL_HOST_USER,
              [toUser],
              fail_silently=False)

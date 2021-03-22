from django.apps import AppConfig
from django.conf import settings
import os

from captionner.captionner import Captionner


class CaptionnerConfig(AppConfig):
    name = 'captionner'
    path = os.path.join(settings.BASE_DIR, "static", "captionner/")
    loaded_model = Captionner(path, "captionnista.pth.tar", "vocab.pickle")

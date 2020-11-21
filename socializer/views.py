from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['instagram'] = user.instagram.username if hasattr(user, 'instagram') else None
        token['email'] = user.username
        token['instagram_picture'] = user.instagram.picture if hasattr(user, 'instagram') else None
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
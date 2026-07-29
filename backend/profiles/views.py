from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile
from .serializers import UserProfileSerializer


class ProfileView(APIView):
    def get(self, request):
        serializer = UserProfileSerializer(UserProfile.current())
        return Response(serializer.data)

    def post(self, request):
        profile = UserProfile.current()
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'calorie_target',
            'dietary_preferences',
            'allergies',
            'foods_to_avoid',
            'created_at',
            'updated_at',
        ]

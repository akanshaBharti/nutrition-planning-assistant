from django.db import models


class UserProfile(models.Model):
    calorie_target = models.PositiveIntegerField(default=2000)
    dietary_preferences = models.JSONField(default=list, blank=True)
    allergies = models.JSONField(default=list, blank=True)
    foods_to_avoid = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def current(cls):
        profile, _ = cls.objects.get_or_create(pk=1)
        return profile

    def __str__(self):
        return f"Profile target: {self.calorie_target} kcal"

# Create your models here.

from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    mobile = models.CharField(max_length=15, blank=True, null=True)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

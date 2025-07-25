# backend/core_app/backends.py

from django.contrib.auth.backends import ModelBackend
from .models import CustomUser # Import CustomUser Anda

class PersonalNumberBackend(ModelBackend):
    def authenticate(self, request, personal_number=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(personal_number=personal_number)
        except CustomUser.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
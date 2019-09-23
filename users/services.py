from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.authtoken.models import Token

UserModel = get_user_model()

class UserCreation:

    user_manager = UserModel.objects
    token_manager = Token.objects

    def create_user(self, first, last, username, email, password):
        with transaction.atomic():
            user = self.user_manager.create(first_name=first,last_name=last,username=username,email=email)
            user.set_password(password)
            user.save()
            token = self.token_manager.create(user=user)
            return user, token

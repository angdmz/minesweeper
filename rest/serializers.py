from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model

from users.services import UserCreation

UserModel = get_user_model()

class UserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_creator = UserCreation()

    def create(self, validated_data):
        username = validated_data['username']
        first = validated_data.get('first_name','')
        last = validated_data.get('last_name','')
        email = validated_data.get('email','')

        user, _ = self.user_creator.create_user(first, last, username, email, validated_data['password'])
        return user

    class Meta:
        model = UserModel
        fields = (
                  'id',
                  'first_name',
                  'last_name',
                  'username',
                  'email',
                  'password',
        )
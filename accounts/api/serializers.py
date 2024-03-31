from django.contrib.auth import get_user_model
from rest_framework import serializers

from user_profile.models import UserProfile

User = get_user_model()


class AllUsersProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'user_id',
            'gender',
            'photo',
            'phone',
        ]

class AllUsersSerializer(serializers.ModelSerializer):
    personal_info = AllUsersProfileSerializer(many=False)
    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'first_name',
            'last_name',
            'user_type',

            'personal_info'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    personal_info = AllUsersProfileSerializer(many=False)
    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'first_name',
            'last_name',
            'user_type',

            'personal_info'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def save(self):
        user = User(
            email=self.validated_data['email'].lower(),
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],

        )
        password = self.validated_data['password']
        # password2 = self.validated_data['password2']
        # if password != password2:
        #     raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(password)
        user.is_active = True
        user.save()

        return user




class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

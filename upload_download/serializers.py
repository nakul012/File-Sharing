from upload_download.models import User, FileUpload
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        username = data["username"]
        password = data["password"]

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data["user"] = user
                else:
                    raise ValidationError("User is deactivated")
            else:
                raise ValidationError("Unable to login with given credentials")
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):

        user = User.objects.create(
            email=validated_data["email"],
            username=validated_data["username"],
            password=make_password(validated_data["password"])
        )
        return user


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:

        model = FileUpload
        fields = '__all__'


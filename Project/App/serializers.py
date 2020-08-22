# https://iheanyi.com/journal/user-registration-authentication-with-django-django-rest-framework-react-and-redux/
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
	username = serializers.CharField(
			max_length=32,
			validators=[UniqueValidator(queryset=User.objects.all())]
			)
	password = serializers.CharField(min_length=8,write_only=True)

	def create(self, validated_data):
		# Do not convert to lowercase here.Do it in signup view
		user = User.objects.create_user(validated_data['username'])
		# GOLD:DND:One should set the password ONLY after creating the user
		# https://stackoverflow.com/a/42109301/9217577
		user.set_password(validated_data['password'])
		user.save()
		return user

	class Meta:
		model = User
		fields = ('username', 'password')

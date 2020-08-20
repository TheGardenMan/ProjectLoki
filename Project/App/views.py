from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes,api_view
from .serializers import UserSerializer

class UserCreate(APIView):
	def post(self, request, format='json'):
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			user = serializer.save()
			if user:		
				token = Token.objects.create(user=user)
				json = serializer.data
				json['token'] = token.key
				return Response(json, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Logout(APIView):
	# caveat:While sending the GET req,include your token in Header as 
	# "Authorization : Token dahjad3fhhblah blah.."
	# Only using that token, user is identified and token is deleted from table.Hence during login,new token has to be generated.
	def get(self, request, format=None):
		try:
			request.user.auth_token.delete()
		except Exception as e:
			# Since req doesn't have token,we can't del it
			return Response(status=status.HTTP_400_BAD_REQUEST)
		else:
			# Return OK
			return Response(status=status.HTTP_200_OK)


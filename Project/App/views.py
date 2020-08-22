from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import permission_classes,api_view,authentication_classes,renderer_classes
from .serializers import UserSerializer
from . import db_handle

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


#Below api_view is must for all functions which respond to an API using "Response"
@api_view(['POST'])
#Response will be in JSON format
@renderer_classes([JSONRenderer]) 
def username_check(request):
	try:
		isAvailable=db_handle.username_check(request.POST.get("username").lower())
		result={'f':isAvailable} #Return 0 or 1 as result
		return Response(result,status=status.HTTP_200_OK)
	except Exception as e:
		print("Username check errors",e)
		return Response(status=status.HTTP_400_BAD_REQUEST)



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




#Below api_view is must for all functions which respond to an API using "Response"
@api_view(['GET'])
@permission_classes([IsAuthenticated])
#Identify a user using his token
# request.user.id request.user.username
def me(request):
	return Response(request.user.id,status=status.HTTP_200_OK)
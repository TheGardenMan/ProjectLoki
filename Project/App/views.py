from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import permission_classes,api_view,authentication_classes,renderer_classes
from .serializers import UserSerializer
from . import db_handle
from . import s3_handle
# request.user.id request.user.username

#Below api_view is must for all functions which respond to an API using "Response".POST means only POST requests are accepted.
@api_view(['POST'])
#Response will be in JSON format
@renderer_classes([JSONRenderer]) 
def username_check(request):
	try:
		print(request.data)
		isAvailable=db_handle.username_check(request.data["username"].lower())
		return Response(isAvailable,status=status.HTTP_200_OK)
	except Exception as e:
		print("Username check errors",e)
		return Response(status=status.HTTP_400_BAD_REQUEST)


class UserCreate(APIView):
	def post(self, request, format='json'):
		# lowercasing the username so that someone cant get a username with caps.Django treats ABC and abc as two diff usernames which is wrong.Hence we force usernames to be small
		# You cant modify request.data since it is QueryDict type
		temp_data=request.data.dict()
		temp_data['username']=temp_data['username'].lower()
		serializer = UserSerializer(data=temp_data)
		if serializer.is_valid():
			user = serializer.save()
			if user:		
				token = Token.objects.create(user=user)
				json = serializer.data
				json['token'] = token.key
				return Response(json, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Below api_view is must for all functions which respond to an API using "Response".POST means only POST requests are accepted.
@api_view(['POST'])
#Response will be in JSON format
@renderer_classes([JSONRenderer]) 
# Make sure he's logged in
@permission_classes([IsAuthenticated])
def follow(request):
	# Check that not sending request to himself
	if request.user.id!=int(request.data['user_id']):
		result=db_handle.follow(request.user.id,int(request.data['user_id']))
		if result==1:
			return Response(status=status.HTTP_200_OK)
		return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	# Dont try to follow yourself
	return Response(status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def accept_follow_request(request):
	if request.user.id!=int(request.data['user_id']):
		# follower_id,followee_id format.
		result=db_handle.accept_follow_request(int(request.data['user_id']),request.user.id)
		if result==1:
			return Response(status=status.HTTP_200_OK)
		return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	# Dont try to accept ur own req
	return Response(status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def unfollow(request):
	result=db_handle.unfollow(request.user.id,int(request.data['user_id']))
	if result==1:
		return Response(status=status.HTTP_200_OK)
	return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def follow_requests_sent(request):
	result=db_handle.follow_requests_sent(request.user.id)
	if result!=0 and len(result)>0:
		return Response(result,status=status.HTTP_200_OK)
	return Response(0,status=status.HTTP_200_OK)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def delete_sent_follow_request(request):
	result=db_handle.delete_sent_follow_request(request.user.id,int(request.data['user_id']))
	if result==1:
		return Response(status=status.HTTP_200_OK)
	return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def followees(request):
	result=db_handle.followees(request.user.id)
	if result!=0 and len(result):
		return Response(result,status=status.HTTP_200_OK)
	return Response(0,status=status.HTTP_200_OK)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def accepted_follow_requests(request):
	results=0 #placeholder
	if request.data["bottom_flag"]:
		results=db_handle.accepted_follow_requests(request.user.id,request.data["bottom_flag"])
	else:
		results=db_handle.accepted_follow_requests(request.user.id)
	return Response(results,status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def follow_requests_received(request):
	results=db_handle.follow_requests_received(request.user.id)
	return Response(results,status=status.HTTP_200_OK)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def delete_received_follow_request(request):
	if db_handle.delete_received_follow_request(request.user.id,request.data['user_id'])==1:
		return Response(status=status.HTTP_200_OK)
	return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def delete_follower(request):
	if db_handle.delete_follower(request.user.id,request.data['user_id'])==1:
		return Response(status=status.HTTP_200_OK)
	return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def followers(request):
	results=db_handle.followers(request.user.id)
	return Response(results,status=status.HTTP_200_OK)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def update_user_location(request):
	result=db_handle.update_user_location(request.user.id,request.data['longitude'],request.data['latitude'])
	if result==1:
		return Response(result,status=status.HTTP_200_OK)
	return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def find_nearby_people(request):
	results=db_handle.find_nearby_people(request.user.id)
	return Response(results,status=status.HTTP_200_OK)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def follow_status(request):
	result=db_handle.follow_status(request.user.id,request.data['user_id'])
	return Response(result,status=status.HTTP_200_OK)


# @api_view(['POST'])
# @renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
class Logout(APIView):
	# caveat:While sending the GET req,include your token in Header as 
	# "Authorization : Token dahjad3fhhblah blah.."
	# Only using that token, user is identified and token is deleted from table.Hence during login,new token has to be generated.
	def post(self, request, format=None):
		try:
			request.user.auth_token.delete()
		except Exception as e:
			# Since req doesn't have token,we can't del it
			return Response(status=status.HTTP_400_BAD_REQUEST)
		else:
			# Return OK
			return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])
def whoami(request):
	content={'name':request.user.username,'id':request.user.id}
	return Response(content,status=status.HTTP_200_OK)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def get_username(request):
	result=db_handle.get_username(request.data["user_id"])
	if result!=0:
		return Response(result,status=status.HTTP_200_OK)
	return Response(0,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def public_post_request(request):
	new_post_id=db_handle.get_new_public_post_id(request.user.id)
	if new_post_id==0:
		return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	public_post_filename=''.join(['public_',str(request.user.id),'_',str(new_post_id),'.jpg'])
	print(public_post_filename)
	public_post_url=s3_handle.get_upload_url(public_post_filename)
	if public_post_url==0:
		return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	result={'filename':public_post_filename,'url':public_post_url}
	return Response(result,status=status.HTTP_200_OK)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def public_post_success(request):
	result=db_handle.public_post_success(request.user.id,request.data["public_post_id"],request.data["longitude"],request.data["latitude"])
	if result==0:
		return Response("primary_key_violation_I_think!",status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def private_post_request(request):
	new_post_id=db_handle.get_new_private_post_id(request.user.id)
	if new_post_id==0:
		return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	private_post_filename=''.join(['private/',str(request.user.id),'_',str(new_post_id),'.jpg'])
	private_post_url=s3_handle.get_upload_url(private_post_filename)
	if private_post_url==0:
		return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	result={'filename':private_post_filename,'url':private_post_url}
	return Response(result,status=status.HTTP_200_OK)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def private_post_success(request):
	# pvt post doesn't need location.
	result=db_handle.private_post_success(request.user.id,request.data["private_post_id"])
	if result==0:
		return Response("primary_key_violation_I_think!",status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	return Response(status=status.HTTP_200_OK)

# Front-end updates user's location to user_last_location.Then it requests for public feed.Backend assumes frontend has already updated the location.
# prev_public_post_id,prev_user_id

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def public_feed(request):
	post_details=[]
	if not request.data["lastpost_user_id"]:
		post_details=db_handle.public_feed(request.user.id)
	else:
		post_details=db_handle.public_feed(request.user.id,int(request.data['lastpost_user_id']),int(request.data['lastpost_post_id']))
	return Response(post_details,status=status.HTTP_200_OK)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def public_post_action(request):
	result=db_handle.public_post_action(request.data["user_id"],request.data["public_post_id"],request.data["action"])
	if result:
		return Response(status=status.HTTP_200_OK)
	return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def delete_public_post(request):
	# ToDo client sends token already.Do we need user_id too?
	if request.user.id==int(request.data["user_id"]):
		result=db_handle.delete_file(request.data["user_id"],request.data["public_post_id"])
		if result==1:
			return Response(status=status.HTTP_200_OK)
		return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def public_posts(request):
	result=db_handle.public_posts(request.user.id)
	if result==0:
		return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	if len(result)==0:
		return Response(0,status=status.HTTP_200_OK)
	return Response(result,status=status.HTTP_200_OK)



@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def new_public_post_check(request):
	result=db_handle.new_public_post_check(request.data["user_id"],request.data["public_post_id"])
	if result==-1:
		return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	return Response(result,status=status.HTTP_200_OK)
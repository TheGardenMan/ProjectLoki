from django.urls import path,include
from App import views
from rest_framework.authtoken.views import obtain_auth_token
# Don't use rest_auth for logout.It doesn't delete token in server.It's useless.
# Don't use rest_auth for login."obtain_auth_token" is simpler
#  Warn: Use rest_auth only for changing the password,Add it to settings before using
urlpatterns = [
	path('whoami/',views.whoami),
	path('signup/',views.UserCreate.as_view()),
	path('login/', obtain_auth_token),
	path('logout/',views.Logout.as_view()),
	path('username_check/',views.username_check),
	path('follow/',views.follow),
	path('accept_follow_request/',views.accept_follow_request),
	path('unfollow/',views.unfollow),
	path('follow_requests_sent/',views.follow_requests_sent),
	path('delete_sent_follow_request/',views.delete_sent_follow_request),
	path('followees/',views.followees),
	path('accepted_follow_requests/',views.accepted_follow_requests),
	path('follow_requests_received/',views.follow_requests_received),
	path('delete_received_follow_request/',views.delete_received_follow_request),
	path('delete_follower/',views.delete_follower),
	path('followers/',views.followers),
	path('update_user_location/',views.update_user_location),
	path('find_nearby_people/',views.find_nearby_people),
	path('follow_status/',views.follow_status),
	path('get_username/',views.get_username),
	path('public_post_request/',views.public_post_request),
	path('public_post_success/',views.public_post_success),
	path('private_post_request/',views.private_post_request),
	path('private_post_success/',views.private_post_success),
	]

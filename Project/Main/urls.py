from django.urls import path,include
from App import views
from rest_framework.authtoken.views import obtain_auth_token
# Don't use rest_auth for logout.It doesn't delete token in server.It's useless.
# Don't use rest_auth for login."obtain_auth_token" is simpler
#  Warn: Use rest_auth only for changing the password,Add it to settings before using
urlpatterns = [
	path('signup/',views.UserCreate.as_view()),
	path('login/', obtain_auth_token),
	path('logout/',views.Logout.as_view()),
	path('username_check/',views.username_check),
	]

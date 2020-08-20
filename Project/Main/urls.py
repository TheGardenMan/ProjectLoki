from django.urls import path,include
from App import views
from rest_framework.authtoken.views import obtain_auth_token
import rest_auth
# Don't use rest_auth for logout.It doesn't delete token in server.It's useless.
# Don't use rest_auth for login."obtain_auth_token" is simpler
#  Use rest_auth only for changing the password
urlpatterns = [
	path('signup/',views.UserCreate.as_view()),
	path('login/', obtain_auth_token),
	path('logout/',views.Logout.as_view()),
	]

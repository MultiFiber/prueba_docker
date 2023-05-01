from django.urls import re_path, path, include
from .views import RefreshJWT, ObtainJWT, Auth


urlpatterns = [
    re_path(r'(?P<version>[-\w]+)/signin', Auth.as_view({'post': 'signin'})),
    re_path(r'(?P<version>[-\w]+)/signup', Auth.as_view({'post': 'signup'})),
    re_path(r'(?P<version>[-\w]+)/signout',Auth.as_view({'get': 'signout'})),
    re_path(r'(?P<version>[-\w]+)/jwt_signin', ObtainJWT.as_view()),
    re_path(r'(?P<version>[-\w]+)/jwt_signin', RefreshJWT.as_view()),
    path('v1/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]
from django.urls import path, include
from rest_framework import routers

from .views import UserViewSet
# from .views import LoginGetTokenView, LogoutDeleteTokenView

app_name = 'users'

router_user = routers.DefaultRouter()
router_user.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router_user.urls)),
    path('auth/', include('djoser.urls.authtoken'))

]

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import views, viewsets, status, exceptions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from .serializers import UserSerializer, UserCreateSerializer, PasswordChangeSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination


    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get',], url_path='me')
    def get_current_user(self, request):
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated(
                code=status.HTTP_401_UNAUTHORIZED
            )
        return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post',], url_path='set_password')
    def set_password(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            raise exceptions.NotAuthenticated(
                code=status.HTTP_401_UNAUTHORIZED
            )
        serializer = PasswordChangeSerializer(instance=user, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
            



     
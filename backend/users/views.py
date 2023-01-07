from pprint import pprint
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import views, viewsets, status, exceptions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from .pagination import CustomPageNumberPagination
from .serializers import UserSerializer, UserCreateSerializer
from .serializers import PasswordChangeSerializer, FollowSerializer
from .models import Follow

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPageNumberPagination


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
            
    @action(detail=False, methods=['get',], url_path='subscriptions')
    def get_subscriptions(self, request):
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated(
                code=status.HTTP_401_UNAUTHORIZED
            )
        
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)

        recipes_limit = request.query_params.get('recipes_limit')
        serializer = FollowSerializer(
            instance=page,
            many=True,
            context={
                'recipes_limit': recipes_limit,
                'request': request
            }
        )

        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        subscription = Follow.objects.filter(
            author=author,
            user=request.user
        )
        is_post = (request.method == 'POST')
        if is_post and author == request.user:
            error = {
                'errors': ('Cannot subscribe to yourself')
            }
            return Response(error, status.HTTP_400_BAD_REQUEST)
        if is_post == subscription.exists():
            error = {
                'errors': (f'{author} subscription is already {is_post}')
            }
            return Response(error, status.HTTP_400_BAD_REQUEST)


        if not is_post:
            subscription.delete()
            return Response(None, status.HTTP_204_NO_CONTENT)
        else:
            Follow.objects.create(
                author=author,
                user=request.user
            )
            data = FollowSerializer(author).data
            data['is_subscribed'] = True
            return Response(data, status.HTTP_201_CREATED)


     
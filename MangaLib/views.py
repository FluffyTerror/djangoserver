from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from django.shortcuts import render
from rest_framework import generics, viewsets, mixins, status, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
import jwt, datetime
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Manga, Category
from .serializers import UserSerializer, MangaSerializer


class MangaListView(generics.ListAPIView):  # GET все тайтлы
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer


class MangaCreateView(APIView):  # POST add manga
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = MangaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


class MangaDetailView(generics.RetrieveAPIView): # GET конкретный тайтл
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer


class MangaUpdateView(generics.UpdateAPIView):  # PUT change attr in manga
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer








class CustomUserCreate(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







class CustomUserLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format='json'):
        email = request.data.get('email')
        password = request.data.get('password')

        if email and password:
            user = User.objects.filter(email=email).first()

            if user and user.check_password(password):
                refresh = RefreshToken.for_user(user)
                tokens = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                return Response(tokens, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)



class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')

            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            user = get_user_model().objects.get(id=token['user_id'])
            user.refresh_token = None  # Удаление refresh token из базы данных
            user.save()

            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)

        except (TokenError, InvalidToken, get_user_model().DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
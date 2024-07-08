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
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Manga, Category
from .serializers import UserSerializer, MangaSerializer


class MangaListView(generics.ListAPIView):  # GET все тайтлы
    #permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer


class MangaCreateView(APIView):  # POST add manga
    #permission_classes = [IsAuthenticated]

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
    #permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer




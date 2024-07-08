from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from MangaLib.views import *


urlpatterns = [
    path('admin/', admin.site.urls),

 #   path('api/v1/register', UserRegister.as_view()),
  #  path('api/v1/login', UserLogin.as_view()),
    path('manga/create/', MangaCreateView.as_view(), name='manga-create'),
    path('manga/', MangaListView.as_view(), name='manga-list'),
    path('manga/<int:pk>/', MangaDetailView.as_view(), name='manga-detail'),
    path('manga/<int:pk>/update/', MangaUpdateView.as_view(), name='manga-update'),

    #path('register/', UserRegistrationView.as_view(), name='register'),
    #path('login/', UserLoginView.as_view(), name='login'),
    #path('user/', UserView.as_view(), name='user'),
    #path('logout/', LogoutView.as_view(), name='logout'),






    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

]

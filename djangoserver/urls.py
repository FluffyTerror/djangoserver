from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from MangaLib.views import *


urlpatterns = [
    path('admin/', admin.site.urls),


    path('manga/create/', MangaCreateView.as_view(), name='manga-create'),
    path('manga/', MangaListView.as_view(), name='manga-list'),
    path('manga/<int:pk>/', MangaDetailView.as_view(), name='manga-detail'),
    path('manga/<int:pk>/update/', MangaUpdateView.as_view(), name='manga-update'),
    path('user/',UserListView.as_view(),name='user-list'),
    path('user/<int:pk>/',UserUpdateView.as_view(),name='user-update'),
    path('manga/add_favourite/', AddFavouriteView.as_view(), name='manga-favourite'),
    path('manga/add_bookmark/', AddBookmarkView.as_view(), name='manga-bookmark'),
    path('manga/<int:manga_id>/add_review/', AddReviewView.as_view(), name='add-review'),
    path('manga/<int:manga_id>/reviews/', MangaReviewsView.as_view(), name='manga-reviews'),

    #path('register/', UserRegistrationView.as_view(), name='register'),
    #path('login/', UserLoginView.as_view(), name='login'),
    #path('user/', UserView.as_view(), name='user'),
    #path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', CustomUserCreate.as_view(), name="create_user"),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('login/', CustomUserLogin.as_view(), name='user-login'),






    path('get_token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
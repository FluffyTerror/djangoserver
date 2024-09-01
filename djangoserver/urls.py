from django.contrib import admin
from django.urls import path
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

    path('profile/', ProfileView.as_view(), name='profile view'),
    path('user/update/', UserUpdateView.as_view(), name='user-update'),
    path('user/', UsernameView.as_view(), name='user_view'),
    path('user_img/<str:username>/', Userimg.as_view(), name='user_image'),
    path('user/<str:username>/bookmarks/', UsernameBookmarksView.as_view(), name='username-bookmarks'),


    path('news/', NewsListView.as_view(), name='news-list'),
    path('news/create/', NewsCreateView.as_view(), name='news-create'),
    path('news/<int:id>/', NewsDetailView.as_view(), name='news-detail'),


    path('manga/find/', MangaIdView.as_view(), name='manga-get-by-id'),
    path('manga/create/', MangaCreateView.as_view(), name='manga-create'),
    path('manga/', MangaListView.as_view(), name='manga-list'),
    path('manga/<int:pk>/', MangaDetailView.as_view(), name='manga-detail'),
    path('manga/<int:pk>/update/', MangaUpdateView.as_view(), name='manga-update'),
    path('manga/add_favourite/', AddFavouriteView.as_view(), name='manga-favourite'),
    path('manga/add_bookmark/', AddBookmarkView.as_view(), name='manga-bookmark'),
    path('manga/<int:manga_id>/add_review/', AddOrUpdateReviewView.as_view(), name='add_or_update_review'),
    path('manga/<int:manga_id>/reviews/', MangaReviewsView.as_view(), name='manga-reviews'),
    #path('review/<int:pk>/update/', UpdateReviewView.as_view(), name='update_review'),
    path('upload_manga/<int:manga_id>/', MangaUploadView.as_view(), name='upload_manga'),



    path('popular_manga/', AllPopularMangaView.as_view(), name='popular page'),
    path('popular/', PopularMangaView.as_view(), name='popular on main page'),
    path('new/', NewReleasesView.as_view(), name='new on main page'),
    path('catalog/', CatalogListView.as_view(), name='catalog page'),


    path('tags/', CategoryListView.as_view(), name='tags-list'),
    path('statuses/', StatusListView.as_view(), name='status-list'),

    path('add_person/', PersonCreateView.as_view(), name="add person"),
    path('authors/', AuthorListView.as_view(), name="authors list"),
    path('publishers/', PublisherListView.as_view(), name="publishers list"),
    path('artists/', ArtistListView.as_view(), name="artists list"),


    path('register/', CustomUserCreate.as_view(), name="create_user"),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('login/', CustomUserLogin.as_view(), name='user-login'),


    path('search/title/', MangaTitleSearchView.as_view(), name='title search'),
    path('search/author/', MangaAuthorSearchView.as_view(), name='author search'),
    path('search/publisher/', MangaPublisherSearchView.as_view(), name='publisher search'),


    path('<int:manga_id>/approve_manga/',ApproveMangaView.as_view(),name= 'manga approve'),
    path('<int:person_id>/approve_person/', ApprovePersonView.as_view(), name='person approve'),

    path('manga/<int:manga_id>/volumes/', MangaVolumesAndChaptersView.as_view(), name='manga-volumes-and-chapters'),
    path('manga_read/<int:manga_id>/', MangaPageDetailView.as_view(), name='manga-page-detail'),

    path('get_token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

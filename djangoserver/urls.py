from django.contrib import admin
from django.urls import path, re_path
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

    path('api/profile/', ProfileView.as_view(), name='profile view'),
    path('api/user/update/', UserUpdateView.as_view(), name='user-update'),
    path('api/user/', UsernameView.as_view(), name='user_view'),
    path('api/user_img/<str:username>/', Userimg.as_view(), name='user_image'),
    path('api/user/<str:username>/bookmarks/', UsernameBookmarksView.as_view(), name='username-bookmarks'),

    path('api/news/', NewsListView.as_view(), name='news-list'),
    path('api/news/create/', NewsCreateView.as_view(), name='news-create'),
    path('api/news/<int:id>/', NewsDetailView.as_view(), name='news-detail'),

    path('api/manga/find/', MangaIdView.as_view(), name='manga-get-by-id'),
    path('api/manga/create/', MangaCreateView.as_view(), name='manga-create'),
    path('api/manga/', MangaListView.as_view(), name='manga-list'),
    path('api/manga/<int:pk>/', MangaDetailView.as_view(), name='manga-detail'),
    path('api/manga/<int:pk>/update/', MangaUpdateView.as_view(), name='manga-update'),
    path('api/manga/add_favourite/', AddFavouriteView.as_view(), name='manga-favourite'),
    path('api/manga/add_bookmark/', AddBookmarkView.as_view(), name='manga-bookmark'),
    path('api/manga/<int:manga_id>/add_review/', AddOrUpdateReviewView.as_view(), name='add_or_update_review'),
    path('api/manga/<int:manga_id>/reviews/', MangaReviewsView.as_view(), name='manga-reviews'),
    path('api/upload_manga/<int:manga_id>/', MangaUploadView.as_view(), name='upload_manga'),

    path('api/popular_manga/', AllPopularMangaView.as_view(), name='popular page'),
    path('api/popular/', PopularMangaView.as_view(), name='popular on main page'),
    path('api/new/', NewReleasesView.as_view(), name='new on main page'),
    path('api/catalog/', CatalogListView.as_view(), name='catalog page'),

    path('api/tags/', CategoryListView.as_view(), name='tags-list'),
    path('api/statuses/', StatusListView.as_view(), name='status-list'),

    path('api/add_person/', PersonCreateView.as_view(), name="add person"),
    path('api/authors/', AuthorListView.as_view(), name="authors list"),
    path('api/publishers/', PublisherListView.as_view(), name="publishers list"),
    path('api/artists/', ArtistListView.as_view(), name="artists list"),

    path('api/register/', CustomUserCreate.as_view(), name="create_user"),
    path('api/logout/', LogoutAPIView.as_view(), name='logout'),
    path('api/login/', CustomUserLogin.as_view(), name='user-login'),

    path('api/search/title/', MangaTitleSearchView.as_view(), name='title search'),
    path('api/search/author/', MangaAuthorSearchView.as_view(), name='author search'),
    path('api/search/publisher/', MangaPublisherSearchView.as_view(), name='publisher search'),

    path('api/<int:manga_id>/approve_manga/', ApproveMangaView.as_view(), name='manga approve'),
    path('api/<int:person_id>/approve_person/', ApprovePersonView.as_view(), name='person approve'),

    path('api/manga/<int:manga_id>/volumes/', MangaVolumesAndChaptersView.as_view(), name='manga-volumes-and-chapters'),
    path('api/manga_read/<int:manga_id>/', MangaPageDetailView.as_view(), name='manga-page-detail'),

    path('api/get_token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('', index,name='index'),
    #re_path(r'^.*$', index, name='index'),
    path('home/', index,name='index'),



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

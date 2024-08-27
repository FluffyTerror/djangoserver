import os
from datetime import datetime, timedelta
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.db.models import Q,Count
from django.http import Http404, HttpResponse
from rest_framework import generics, status, views
from rest_framework.generics import get_object_or_404, ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Manga, Review, News, Category
from .serializers import UserSerializer, MangaSerializer, ReviewSerializer, MangaZipSerializer, NewsSerializer, \
    CategorySerializer


class UsernameBookmarksView(APIView):
    def post(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Получаем закладки пользователя
        bookmarks = user.bookmarks.all()

        # Извлекаем параметры для сортировки
        sort_by = request.data.get('sort_by', 'popularity')  # По умолчанию сортировка по популярности
        status_filter = request.data.get('status', [])  # По умолчанию фильтр по статусу пустой список


        if status_filter:
            bookmarks = bookmarks.filter(Status__in=status_filter)
        # Применяем сортировку
        if sort_by == 'chapters':
            bookmarks = bookmarks.order_by('-Chapters')
        elif sort_by == 'release_date':
            bookmarks = bookmarks.order_by('-Release')
        elif sort_by == 'update_date':
            bookmarks = bookmarks.order_by('-Created_at')
        elif sort_by == 'add_date':
            bookmarks = bookmarks.order_by('-id')
        elif sort_by == 'title_az':
            bookmarks = bookmarks.order_by('Title')
        elif sort_by == 'title_za':
            bookmarks = bookmarks.order_by('-Title')

        # Сериализуем данные
        serializer = MangaSerializer(bookmarks, many=True)
        return Response(serializer.data)






class CatalogListView(APIView):
    def post(self, request):
        sort_by = request.data.get('sort_by', 'popularity')  # По умолчанию сортировка по популярности
        status_filter = request.data.get('status', [])  # По умолчанию фильтр по статусу пустой список
        category_filter = request.data.get('category', [])  # По умолчанию фильтр по категории пустой список

        # Начинаем с базового QuerySet
        queryset = Manga.objects.all()

        # Фильтрация по статусу (если статусы переданы)
        if status_filter:
            queryset = queryset.filter(Status__in=status_filter)

        # Фильтрация по категориям
        if category_filter:
            queryset = queryset.filter(Category__name__in=category_filter).distinct()

        # Сортировка
        if sort_by == 'popularity':
            queryset = queryset.annotate(popularity=Count('bookmarked_users')).order_by('-popularity')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-Rating')
        elif sort_by == 'chapters':
            queryset = queryset.order_by('-Chapters')
        elif sort_by == 'release_date':
            queryset = queryset.order_by('-Release')
        elif sort_by == 'update_date':
            queryset = queryset.order_by('-Created_at')
        elif sort_by == 'add_date':
            queryset = queryset.order_by('-id')
        elif sort_by == 'title_az':
            queryset = queryset.order_by('Title')
        elif sort_by == 'title_za':
            queryset = queryset.order_by('-Title')

        serializer = MangaSerializer(queryset, many=True)
        return Response(serializer.data)

class StatusListView(APIView):
    def get(self, request, *args, **kwargs):
        statuses = [
            {"name": "Завершен"},
            {"name": "Анонс"},
            {"name": "Приостановлен"},
            {"name": "Выпуск прекращен"},
            {"name": "Выходит"}
        ]
        return Response(statuses, status=status.HTTP_200_OK)


class NewsDetailView(RetrieveAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    lookup_field = 'id'


class NewsCreateView(CreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def perform_create(self, serializer):
        serializer.save(User=self.request.user)

class NewsListView(ListAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

class MangaUploadView(views.APIView):
    def post(self, request, manga_id):
        try:
            manga = Manga.objects.get(id=manga_id)
        except Manga.DoesNotExist:
            return Response({'error': 'Manga not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = MangaZipSerializer(data=request.data, context={'manga_id': manga_id})
        if serializer.is_valid():
            manga = serializer.save()
            return Response({'message': 'Manga uploaded successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class MangaIdView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        manga_id = request.data.get('id')
        if not manga_id:
            return Response({"error": "No ID provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            manga = Manga.objects.get(id=manga_id)
        except Manga.DoesNotExist:
            return Response({"error": "Manga not found"}, status=status.HTTP_404_NOT_FOUND)

        # Сериализация манги
        manga_serializer = MangaSerializer(manga)

        # Ищем отзыв текущего пользователя, если пользователь аутентифицирован
        user_review = None
        is_in_bookmarks = False
        if request.user.is_authenticated:
            try:
                user_review = Review.objects.get(user=request.user, manga=manga)
                user_review_serializer = ReviewSerializer(user_review)
            except Review.DoesNotExist:
                user_review_serializer = None

            # Проверяем, есть ли тайтл в закладках пользователя
            is_in_bookmarks = manga in request.user.bookmarks.all()

        # Подготавливаем ответ
        response_data = {
            "manga": manga_serializer.data,
            "user_review": user_review_serializer.data if user_review_serializer else None,
            "is_in_bookmarks": is_in_bookmarks
        }

        return Response(response_data, status=status.HTTP_200_OK)


class MangaListView(generics.ListAPIView):  # GET все тайтлы
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer


class Userimg(APIView):
    # Разрешаем доступ всем пользователям
    permission_classes = []

    def get(self, request, username=None, *args, **kwargs):
        # Ищем пользователя по username
        user = get_object_or_404(User, username=username)

        # Получаем изображение профиля пользователя
        profile_image = user.profile_image

        if not profile_image:
            raise Http404("User does not have a profile image.")

        # Открываем файл изображения и возвращаем его в ответе
        try:
            with open(profile_image.path, 'rb') as image_file:
                return HttpResponse(image_file.read(), content_type="image/jpeg")
        except FileNotFoundError:
            raise Http404("Image file not found.")



class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        # Получение текущего пользователя из токена
        user = request.user

        # Если пользователь найден, сериализуем его данные
        if user:
            return Response({"username": user.username}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class UsernameView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:
            return Response({"error": "No valid username provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class MangaCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = MangaSerializer(data=request.data)
        if serializer.is_valid():
            manga = serializer.save()

            # Создаем директорию для манги и обложки
            manga_dir = os.path.join('media/Manga', manga.Title)
            cover_dir = os.path.join(manga_dir, 'cover')
            os.makedirs(cover_dir, exist_ok=True)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MangaDetailView(generics.RetrieveAPIView): # GET конкретный тайтл
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer


class MangaUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer

    # Позволяем частичное обновление, чтобы не требовалось передавать все поля
    def partial_update(self, request, *args, **kwargs):
        manga = self.get_object()
        serializer = self.get_serializer(manga, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddBookmarkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        manga_id = request.data.get('manga_id')

        try:
            manga = Manga.objects.get(id=manga_id)
        except Manga.DoesNotExist:
            return Response({"error": "Manga not found"}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, находится ли манга уже в закладках пользователя
        if manga in user.bookmarks.all():
            # Если манга уже в закладках, удаляем её
            user.bookmarks.remove(manga)
            user.save()
            return Response({"status": "Manga removed from bookmarks"}, status=status.HTTP_200_OK)
        else:
            # Если манги нет в закладках, добавляем её
            user.bookmarks.add(manga)
            user.save()
            return Response({"status": "Manga added to bookmarks"}, status=status.HTTP_200_OK)


class AddFavouriteView(APIView):# POST добавить в избранное
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        manga_id = request.data.get('manga_id')
        try:
            manga = Manga.objects.get(id=manga_id)
        except Manga.DoesNotExist:
            return Response({"error": "Manga not found"}, status=status.HTTP_404_NOT_FOUND)

        user.favourite.add(manga)
        user.save()
        return Response({"status": "Manga added to favourite"}, status=status.HTTP_200_OK)


class AddOrUpdateReviewView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        manga_id = self.kwargs['manga_id']
        manga = Manga.objects.get(id=manga_id)

        # Попытка найти существующий отзыв
        try:
            review = Review.objects.get(user=self.request.user, manga=manga)
            # Обновляем существующий отзыв
            review.text = serializer.validated_data['text']
            review.rating = serializer.validated_data['rating']
            review.save()
        except Review.DoesNotExist:
            # Создаем новый отзыв
            review = Review.objects.create(
                user=self.request.user,
                manga=manga,
                text=serializer.validated_data['text'],
                rating=serializer.validated_data['rating']
            )
            # Увеличиваем счетчик отзывов
            manga.RatingCount += 1

        # Пересчитываем средний рейтинг
        all_reviews = manga.reviews.all()
        total_rating = sum([r.rating for r in all_reviews])
        manga.Rating = round(total_rating / manga.RatingCount, 2)
        manga.save()

        serializer.instance = review


class MangaReviewsView(generics.ListAPIView): # GET список отзывов
    permission_classes = [AllowAny]
    serializer_class = ReviewSerializer


    def get_queryset(self):
        manga_id = self.kwargs['manga_id']
        return Review.objects.filter(manga__id=manga_id)



class CustomUserCreate(APIView): # POST создать юзера
    permission_classes = [AllowAny]

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







class CustomUserLogin(APIView):# POST залогинить юзера
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



class LogoutAPIView(APIView):# POST разалогинить юзера
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


class MangaTitleSearchView(APIView):
    def post(self, request, *args, **kwargs):
        query = request.data.get('query', None)

        if query:
            # Поиск по тайтлу, автору и художнику
            mangas = Manga.objects.filter(
                Q(Title__icontains=query)
            ).distinct()

            # Сериализация и возврат данных
            serializer = MangaSerializer(mangas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No query parameter provided"}, status=status.HTTP_400_BAD_REQUEST)



class MangaAuthorSearchView(APIView):
    def post(self, request, *args, **kwargs):
        query = request.data.get('query', None)

        if query:
            # Поиск по тайтлу, автору и художнику
            mangas = Manga.objects.filter(
                Q(Author__icontains=query)
            ).distinct()

            # Сериализация и возврат данных
            serializer = MangaSerializer(mangas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No query parameter provided"}, status=status.HTTP_400_BAD_REQUEST)


class MangaArtistSearchView(APIView):
    def post(self, request, *args, **kwargs):
        query = request.data.get('query', None)

        if query:
            mangas = Manga.objects.filter(
                Q(Artist__icontains=query)
            ).distinct()

            serializer = MangaSerializer(mangas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No query parameter provided"}, status=status.HTTP_400_BAD_REQUEST)



class PopularMangaView(ListAPIView):
    serializer_class = MangaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Сортируем манги по количеству отзывов и рейтингу
        return Manga.objects.order_by('-RatingCount', '-Rating')[:6]  # Топ-6 манг


class AllPopularMangaView(APIView):
    serializer_class = MangaSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        # Получаем параметры из тела запроса
        tags = request.data.get('tags', [])  # список тегов
        time_filter = request.data.get('time_filter')  # фильтр по времени

        # Получаем начальный queryset для манги
        queryset = Manga.objects.all()

        # Фильтрация по тегам
        if tags:
            queryset = queryset.filter(Category__name__in=tags).distinct()

        # Фильтрация по времени
        if time_filter == 'day':
            queryset = queryset.filter(Created_at__gte=datetime.now() - timedelta(days=1))
        elif time_filter == 'week':
            queryset = queryset.filter(Created_at__gte=datetime.now() - timedelta(weeks=1))
        elif time_filter == 'month':
            queryset = queryset.filter(Created_at__gte=datetime.now() - timedelta(days=30))
        elif time_filter == 'year':
            queryset = queryset.filter(Created_at__gte=datetime.now() - timedelta(days=365))

        # Сортировка по количеству отзывов и рейтингу
        queryset = queryset.order_by('-RatingCount', '-Rating')[:100]

        # Получаем все категории (теги)

        # Сериализация данных
        manga_serializer = self.serializer_class(queryset, many=True)

        # Возвращаем результат с мангой и списком тегов
        return Response({
            'manga': manga_serializer.data,
        }, status=status.HTTP_200_OK)




class NewReleasesView(ListAPIView):
    serializer_class = MangaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Возвращаем манги, отсортированные по дате создания (сначала новые)
        return Manga.objects.order_by('-Created_at')[:6]  # Топ-6 новинок



class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Manga,Review
from .serializers import UserSerializer, MangaSerializer, ReviewSerializer


class MangaIdView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        manga_id = request.data.get('id')
        if not manga_id:
            return Response({"error": "No ID provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            manga = Manga.objects.get(id=manga_id)
        except Manga.DoesNotExist:
            return Response({"error": "Manga not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MangaSerializer(manga)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MangaListView(generics.ListAPIView):  # GET все тайтлы
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer


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




class MangaCreateView(APIView):  # POST создать мангу
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = MangaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MangaDetailView(generics.RetrieveAPIView): # GET конкретный тайтл
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer


class MangaUpdateView(generics.UpdateAPIView):  # PUT change attr in manga
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer



class AddBookmarkView(APIView): # POST добавить в закладки
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        manga_id = request.data.get('manga_id')
        try:
            manga = Manga.objects.get(id=manga_id)
        except Manga.DoesNotExist:
            return Response({"error": "Manga not found"}, status=status.HTTP_404_NOT_FOUND)
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


class AddReviewView(generics.CreateAPIView):  # POST создать отзыв
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        manga_id = self.kwargs['manga_id']
        manga = Manga.objects.get(id=manga_id)

        review = serializer.save(user=self.request.user, manga=manga)

        manga.RatingCount += 1
        new_rating = (manga.Rating * (manga.RatingCount - 1) + review.rating) / manga.RatingCount
        manga.Rating = round(new_rating, 2)
        manga.save()



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


class MangaSearchView(APIView):
    def post(self, request, *args, **kwargs):
        query = request.data.get('query', None)

        if query:
            # Поиск по тайтлу, автору и художнику
            mangas = Manga.objects.filter(
                Q(Title__icontains=query) |
                Q(Author__icontains=query) |
                Q(Artist__icontains=query)
            ).distinct()

            # Сериализация и возврат данных
            serializer = MangaSerializer(mangas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No query parameter provided"}, status=status.HTTP_400_BAD_REQUEST)


import os
import zipfile

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password, is_password_usable
from django.core.files.base import ContentFile
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.response import Response


from MangaLib.models import Manga, User, Review, Category, MangaPage, News


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    user_profile_image = serializers.ImageField(source='user.profile_image', read_only=True)
    manga_id = serializers.ReadOnlyField(source='manga.id')
    manga_title = serializers.ReadOnlyField(source='manga.Title')  # Добавляем название манги

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_profile_image', 'text', 'rating', 'created_at', 'manga_id', 'manga_title']


class MangaZipSerializer(serializers.Serializer):
    zip_file = serializers.FileField()
    volume = serializers.IntegerField()
    chapter = serializers.IntegerField()
    chapter_title = serializers.CharField()

    def create(self, validated_data):
        # Получаем ID манги из контекста
        manga_id = self.context.get('manga_id')
        if not manga_id:
            raise serializers.ValidationError("ID манги не передан в контексте.")

        # Находим мангу по ID
        try:
            manga = Manga.objects.get(id=manga_id)
        except Manga.DoesNotExist:
            raise serializers.ValidationError("Манга с таким ID не существует.")

        # Получаем полное название манги
        manga_title = manga.Title
        if not manga_title:
            raise serializers.ValidationError("Название манги не указано.")

        # Основной путь для манги
        manga_dir = os.path.join('media/manga', manga_title)

        # Получаем название тома и главы
        volume = validated_data.get('volume')
        chapter = validated_data.get('chapter')
        chapter_title = validated_data.get('chapter_title')

        # Создаем папки для обложки, томов и глав с использованием полного названия главы
        cover_dir = os.path.join(manga_dir, 'cover')
        volume_dir = os.path.join(manga_dir, f'volume_{volume}')
        # Папка главы теперь будет включать полное название главы
        chapter_dir = os.path.join(volume_dir, f'{chapter_title}')

        # Убедитесь, что папки созданы
        os.makedirs(cover_dir, exist_ok=True)
        os.makedirs(volume_dir, exist_ok=True)
        os.makedirs(chapter_dir, exist_ok=True)

        # Распаковываем ZIP файл
        zip_file = validated_data.get('zip_file')
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # Сначала ищем обложку
            cover_image = None
            for file_name in zip_ref.namelist():
                if file_name.lower().endswith(('cover.jpg', 'cover.jpeg', 'cover.png')):
                    cover_image = zip_ref.read(file_name)
                    break

            # Сохраняем обложку, если она найдена
            if cover_image:
                cover_path = os.path.join(cover_dir, 'cover.jpg')
                with open(cover_path, 'wb') as f:
                    f.write(cover_image)
                # Обновляем поле обложки в модели
                manga.Image = f'manga/{manga_title}/cover/cover.jpg'
                manga.save()

            # Сохраняем страницы манги с нумерацией
            image_files = sorted([file_name for file_name in zip_ref.namelist() if
                                  file_name.endswith(('.jpg', '.jpeg', '.png')) and 'cover' not in file_name.lower()])

            for index, file_name in enumerate(image_files, start=1):
                file_data = zip_ref.read(file_name)
                new_file_name = f"{index}.jpg"
                file_path = os.path.join(chapter_dir, new_file_name)

                # Сохраняем файл
                with open(file_path, 'wb') as f:
                    f.write(file_data)

                # Создаем объект страницы манги
                MangaPage.objects.create(
                    manga=manga,
                    volume=volume,
                    chapter=chapter,
                    page_number=index,
                    page_image=f'manga/{manga_title}/volume_{volume}/chapter_{chapter}_{chapter_title}/{new_file_name}',
                    Chapter_Title=chapter_title  # Сохраняем название главы в поле модели
                )

        return manga

class MangaSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.CharField(max_length=64),
        write_only=True
    )
    categories_display = serializers.SerializerMethodField()
   # reviews = ReviewSerializer(many=True, read_only=True)  # Добавлено поле для отзывов

    class Meta:
        model = Manga
        fields = (
            "id", "Title", "Author", "Description", "Release", "Status",
            "Chapters", "Artist", "categories", "Image", "Rating",
            "RatingCount", "categories_display","Created_at"
        )
        read_only_fields = ("id", "Rating", "RatingCount")

    def get_categories_display(self, obj):
        return [category.name for category in obj.Category.all()]

    def create(self, validated_data):
        # Извлекаем категории из валидированных данных
        categories_data = validated_data.pop('categories')

        # Создаём объект манги
        manga = Manga.objects.create(**validated_data)

        # Добавляем категории к манге
        for category_name in categories_data:
            category, created = Category.objects.get_or_create(name=category_name)
            manga.Category.add(category)

        return manga

    def update(self, instance, validated_data):
        # Извлекаем категории, если они предоставлены
        categories_data = validated_data.pop('categories', None)

        # Обновляем основные поля
        instance.Title = validated_data.get('Title', instance.Title)
        instance.Author = validated_data.get('Author', instance.Author)
        instance.Description = validated_data.get('Description', instance.Description)
        instance.Release = validated_data.get('Release', instance.Release)
        instance.Is_Finished = validated_data.get('Status', instance.Is_Finished)
        instance.Chapters = validated_data.get('Chapters', instance.Chapters)
        instance.Artist = validated_data.get('Artist', instance.Artist)
        instance.Image = validated_data.get('Image', instance.Image)

        # Если категории были переданы, обновляем их
        if categories_data is not None:
            instance.Category.clear()
            for category_name in categories_data:
                category, created = Category.objects.get_or_create(name=category_name)
                instance.Category.add(category)

        # Сохраняем объект манги
        instance.save()

        return instance


class UserSerializer(serializers.ModelSerializer):
    bookmarks = MangaSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_image', 'about', 'password', 'bookmarks', 'reviews', 'favourite']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'profile_image': {'required': False},
            'about': {'required': False},
        }

    def update(self, instance, validated_data):
        # Проверяем, если новый пароль передан и его нужно хешировать
        password = validated_data.get('password', None)
        if password:
            # Проверяем, если пароль не является "используемым" (хешированным)
            if not is_password_usable(instance.password):
                validated_data['password'] = make_password(password)

        return super().update(instance, validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


class UserBriefSerializer(serializers.ModelSerializer):# костыль для новостей
    class Meta:
        model = User
        fields = ['username', 'profile_image']


class NewsSerializer(serializers.ModelSerializer):
    User = UserBriefSerializer(read_only=True)

    class Meta:
        model = News
        fields = ['User','id', 'Title', 'Content', 'Created_at']
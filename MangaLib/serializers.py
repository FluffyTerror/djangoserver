import os
import shutil
import zipfile
from django.core.files.storage import default_storage
from django.contrib.auth.hashers import make_password, is_password_usable
from rest_framework import serializers
from MangaLib.models import Manga, User, Review, Category, MangaPage, News, Person


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    user_profile_image = serializers.SerializerMethodField()  # Используем метод для корректировки пути
    manga_id = serializers.ReadOnlyField(source='manga.id')
    manga_title = serializers.ReadOnlyField(source='manga.Title')  # Добавляем название манги

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_profile_image', 'text', 'rating', 'created_at', 'manga_id', 'manga_title']

    def get_user_profile_image(self, obj):
        if obj.user.profile_image:
            return obj.user.profile_image.url
        return None


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

    def get_Image(self, obj):
        # Приведение пути к относительному формату
        if obj.Image:
            # Убираем домен и возвращаем только относительный путь
            return obj.Image.url
        return None



class MangaSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.CharField(max_length=64),
        write_only=True,
        required=False
    )
    categories_display = serializers.SerializerMethodField()
    Status = serializers.ChoiceField(choices=Manga.STATUS_CHOICES)
    Image = serializers.ImageField(required=False)

    Mod_status = serializers.ChoiceField(choices=Manga.MOD_CHOICES, read_only=True)
    Mod_date = serializers.DateTimeField(read_only=True)  # Поле только для чтения

    class Meta:
        model = Manga
        fields = (
            "id", "Title", "Author", "Description", "Release", "Status",
            "Chapters", "Artist", "categories", "Image", "Rating",
            "RatingCount", "categories_display", "Created_at", "Publisher","Mod_status", "Mod_date","Mod_message", "Url_message"
        )
        read_only_fields = ("id", "Rating", "RatingCount", "Mod_status", "Mod_date")


    def get_categories_display(self, obj):
        return [category.name for category in obj.Category.all()]

    def create(self, validated_data):
        categories_data = validated_data.pop('categories', [])

        manga = Manga.objects.create(**validated_data)

        for category_name in categories_data:
            category, created = Category.objects.get_or_create(name=category_name)
            manga.Category.add(category)

        manga_dir = os.path.join('media/Manga', manga.Title)
        cover_dir = os.path.join(manga_dir, 'cover')
        os.makedirs(cover_dir, exist_ok=True)

        if manga.Image:
            old_image_path = manga.Image.path
            new_image_path = os.path.join(cover_dir, 'cover.jpg')

            shutil.move(old_image_path, new_image_path)
            manga.Image.name = os.path.join('Manga', manga.Title, 'cover', 'cover.jpg')
            manga.save()

        return manga

    def update(self, instance, validated_data):
        old_title = instance.Title
        new_title = validated_data.get('Title', old_title)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if old_title != new_title:
            old_dir = os.path.join('media/Manga', old_title)
            new_dir = os.path.join('media/Manga', new_title)

            if os.path.exists(old_dir):
                shutil.move(old_dir, new_dir)

            if instance.Image and instance.Image.name:
                old_image_path = instance.Image.name
                new_image_path = old_image_path.replace(old_title, new_title)

                old_image_full_path = os.path.join('media', old_image_path)
                new_image_full_path = os.path.join('media', new_image_path)

                if os.path.exists(old_image_full_path):
                    os.makedirs(os.path.dirname(new_image_full_path), exist_ok=True)
                    shutil.move(old_image_full_path, new_image_full_path)

                instance.Image.name = new_image_path

        if 'Image' in validated_data:
            new_image = validated_data['Image']

            manga_dir = os.path.join('media/Manga', instance.Title)
            cover_dir = os.path.join(manga_dir, 'cover')

            if os.path.exists(cover_dir):
                for filename in os.listdir(cover_dir):
                    file_path = os.path.join(cover_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

            os.makedirs(cover_dir, exist_ok=True)

            new_image_path = os.path.join(cover_dir, 'cover.jpg')

            with open(new_image_path, 'wb+') as destination:
                for chunk in new_image.chunks():
                    destination.write(chunk)

            instance.Image.name = os.path.join(instance.Title, 'cover', 'cover.jpg')

        categories_data = validated_data.pop('categories', None)
        if categories_data is not None:
            instance.Category.clear()
            for category_name in categories_data:
                category, created = Category.objects.get_or_create(name=category_name)
                instance.Category.add(category)

        instance.save()

        return instance

    def get_Image(self, obj):
        # Приведение пути к относительному формату для изображения манги
        if obj.Image:
            # Возвращаем относительный путь
            return f'/media/{obj.Image.name}'
        return None


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
        profile_image = serializers.SerializerMethodField()  # Приводим profile_image к относительному пути

    def get_profile_image(self, obj):
        # Приведение пути к относительному формату для изображения профиля пользователя
        if obj.profile_image:
            return obj.profile_image.url  # Возвращаем относительный путь
        return None



class NewsSerializer(serializers.ModelSerializer):
    User = UserBriefSerializer(read_only=True)

    class Meta:
        model = News
        fields = ['User','id', 'Title', 'Content', 'Created_at']



class PersonSerializer(serializers.ModelSerializer):
    Mod_status = serializers.ChoiceField(choices=Person.MOD_CHOICES, read_only=True)
    Mod_date = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Person
        fields = ['id', 'Nickname', 'Country', 'Type', 'About', 'profile_image',"Mod_status", "Mod_date","Mod_message"]
        read_only_fields = ("Mod_status", "Mod_date")
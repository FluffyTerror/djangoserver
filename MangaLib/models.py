import os

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

def manga_cover_directory_path(instance, filename):
    # Обложки манги будут храниться в папке 'media/Manga/{manga_title}/cover/{filename}'
    return f'Manga/{slugify(instance.Title)}/cover/{filename}'

def manga_pages_directory_path(instance, filename):
    # Страницы манги будут храниться в папке 'media/Manga/{manga_title}/volume_{volume}/chapter_{chapter}/{page_number}.jpg'
    return f'Manga/{slugify(instance.manga.Title)}/volume_{instance.volume}/chapter_{instance.chapter}/{filename}'

def user_profile_image_directory_path(instance, filename):
    # Файлы пользователей будут храниться в папке 'media/Users/{user_id}/{filename}'
    return f'Users/{instance.id}/{filename}'



class Manga(models.Model):
    Title = models.CharField(max_length=128)
    Author = models.CharField(max_length=64)
    Description = models.TextField(blank=True)
    Release = models.DateField()
    Status = models.CharField(default=None)
    Chapters = models.IntegerField()
    Artist = models.CharField(max_length=64)
    Image = models.ImageField(upload_to=manga_cover_directory_path, default='Manga/image_10.png')  # Сюда будет загружаться обложка
    Rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    RatingCount = models.IntegerField(default=0)
    Category = models.ManyToManyField(Category, related_name='manga')

    def __str__(self):
        return self.Title

    def save(self, *args, **kwargs):
        # Сохраняем мангу
        super().save(*args, **kwargs)

        # Создаем директорию для страниц манги, если её нет
        manga_dir = os.path.join('media/manga', slugify(self.Title))
        os.makedirs(manga_dir, exist_ok=True)



class MangaPage(models.Model):
    manga = models.ForeignKey(Manga, related_name='pages', on_delete=models.CASCADE)
    page_image = models.ImageField(upload_to=manga_pages_directory_path)
    volume = models.IntegerField(default=1)
    chapter = models.IntegerField(default=1)
    page_number = models.IntegerField(default=1)
    Chapter_Title = models.CharField(max_length=128,default="Chapter title")

    class Meta:
        unique_together = ('manga', 'volume', 'chapter', 'page_image','Chapter_Title')

    def __str__(self):
        return f"Volume {self.volume}, Chapter {self.chapter}, Page {self.page_number} ,Chapter_Title{self.Chapter_Title} "

#





class User(AbstractUser):
    username = models.CharField(max_length=24, unique=True)
    email = models.EmailField(max_length=48, unique=True)
    profile_image = models.ImageField(upload_to=user_profile_image_directory_path, default='Users/User profile picture.png')
    password = models.CharField(max_length=128)
    about = models.CharField(max_length=500, default='Что-то обо мне...')
    bookmarks = models.ManyToManyField(Manga, related_name='bookmarked_users',default=None)
    favourite = models.ManyToManyField(Manga, related_name='favourite_users',default=None)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        # Проверяем, был ли передан новый пароль и нужно ли его хешировать
        if self._state.adding or not self.pk or not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)



    def __str__(self):
        return self.email


class News(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news')
    Title = models.CharField(max_length=255)
    Content = models.TextField()
    Created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Title



class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(max_length=1000)
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.manga.Title}'

    class Meta:
        unique_together = ('user', 'manga')  # Один пользователь может оставить только один отзыв на одну мангу
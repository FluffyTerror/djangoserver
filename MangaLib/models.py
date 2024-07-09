from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):
    username = models.CharField(max_length=24, unique=True)
    email = models.EmailField(max_length=48, unique=True)
    profile_image = models.ImageField(upload_to='media/', default='User profile picture.png')
    password = models.CharField(max_length=128)
    about = models.CharField(max_length=500, default='Что-то обо мне...')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def save(self, *args, **kwargs):
        if not self.pk or not User.objects.filter(pk=self.pk, password=self.password).exists():
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email



class Manga(models.Model):
    Title = models.CharField(max_length=128)
    Author = models.CharField(max_length=64)
    Description = models.TextField(blank=True)
    Release = models.DateField()
    Is_Finished = models.BooleanField(default=True)
    Chapters = models.IntegerField()
    artist = models.CharField(max_length=64)
    Category = models.CharField()
    rating = models.FloatField(default=0)
    ratingCount = models.IntegerField(default=0)
    Image = models.ImageField(upload_to='media/manga', default='image 8.png')


    def __str__(self):
        return self.Title

    def get_categories(self):
        return self.Category.split(',')

class Category(models.Model):
    Category = models.CharField(max_length=64)

    def __str__(self):
        return self.Category



class Reviews(models.Model):
    description = models.CharField(max_length=1000)
    rating = models.FloatField( default=0)
    date_posted = models.DateField()
    manga_title = models.CharField()

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models


class Manga(models.Model):
    Title = models.CharField(max_length=128)
    Author = models.CharField(max_length=64)
    Description = models.TextField(blank=True)
    Release = models.DateField()
    Is_Finished = models.BooleanField(default=True) # change to CharField
    Chapters = models.IntegerField()
    Artist = models.CharField(max_length=64)
    Category = models.CharField()
    Image = models.ImageField(upload_to='media/manga', default='image 8.png')
    Rating = models.FloatField(default=0)
    RatingCount = models.IntegerField(default=0)



    def __str__(self):
        return self.Title

    def get_categories(self):
        return self.Category.split(',')




class User(AbstractUser):
    username = models.CharField(max_length=24, unique=True)
    email = models.EmailField(max_length=48, unique=True)
    profile_image = models.ImageField(upload_to='media/', default='User profile picture.png')
    password = models.CharField(max_length=128)
    about = models.CharField(max_length=500, default='Что-то обо мне...')
    bookmarks = models.ManyToManyField(Manga, related_name='bookmarked_users',default=None)
    favourite = models.ManyToManyField(Manga, related_name='favourite_users',default=None)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.pk or not User.objects.filter(pk=self.pk, password=self.password).exists():
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email




class Category(models.Model):
    Category = models.CharField(max_length=64)

    def __str__(self):
        return self.Category



class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(max_length=1000)
    rating = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.manga.Title}'

    class Meta:
        unique_together = ('user', 'manga')  # Один пользователь может оставить только один отзыв на одну мангу
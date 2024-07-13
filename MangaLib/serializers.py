from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.response import Response


from MangaLib.models import Manga, User, Review, Category


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    user_profile_image = serializers.ImageField(source='user.profile_image', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_profile_image', 'text', 'rating', 'created_at']


class MangaSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.CharField(max_length=64),
        write_only=True
    )
    categories_display = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)  # Добавлено поле для отзывов

    class Meta:
        model = Manga
        fields = (
            "id", "Title", "Author", "Description", "Release", "Is_Finished",
            "Chapters", "Artist", "categories", "Image", "Rating",
            "RatingCount", "categories_display", "reviews"  # Добавлено поле для отзывов
        )
        read_only_fields = ("id",)

    def get_categories_display(self, obj):
        return [category.name for category in obj.Category.all()]

    def create(self, validated_data):
        categories_data = validated_data.pop('categories')
        manga = Manga.objects.create(**validated_data)
        for category_name in categories_data:
            category, created = Category.objects.get_or_create(name=category_name)
            manga.Category.add(category)
        return manga

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', None)
        instance.Title = validated_data.get('Title', instance.Title)
        instance.Author = validated_data.get('Author', instance.Author)
        instance.Description = validated_data.get('Description', instance.Description)
        instance.Release = validated_data.get('Release', instance.Release)
        instance.Is_Finished = validated_data.get('Is_Finished', instance.Is_Finished)
        instance.Chapters = validated_data.get('Chapters', instance.Chapters)
        instance.Artist = validated_data.get('Artist', instance.Artist)
        instance.Image = validated_data.get('Image', instance.Image)
        instance.RatingCount = validated_data.get('RatingCount', instance.RatingCount)
        instance.Rating = validated_data.get('Rating', instance.Rating)

        if categories_data:
            instance.Category.clear()
            for category_name in categories_data:
                category, created = Category.objects.get_or_create(name=category_name)
                instance.Category.add(category)

        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    bookmarks = MangaSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_image', 'about', 'bookmarks', 'reviews', 'favourite']
        extra_kwargs = {
            'profile_image': {'required': False},
            'about': {'required': False},
        }

    def save(self, *args, **kwargs):
        # Хеширование пароля перед сохранением
        if not self.pk or not User.objects.filter(pk=self.pk, password=self.password).exists():
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']
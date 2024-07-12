from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.response import Response


from MangaLib.models import Manga, User, Review


class MangaSerializer(serializers.ModelSerializer):
    Category = serializers.ListField(
        child=serializers.CharField(max_length=64),
        source='get_categories',
        write_only=True
    )
    Category_display = serializers.CharField(source='Category', read_only=True)

    class Meta:
        model = Manga
        fields = ("Title", "Author", "Description", "Release", "Is_Finished", "Chapters", "Artist", "Category","Image", "Rating", "RatingCount","Category_display")

    def create(self, validated_data):
        categories = validated_data.pop('get_categories', [])
        validated_data['Category'] = ','.join(categories)
        return Manga.objects.create(**validated_data)

    def update(self, instance, validated_data):
        categories = validated_data.pop('get_categories', instance.Category.split(','))
        instance.Title = validated_data.get('Title', instance.Title)
        instance.Author = validated_data.get('Author', instance.Author)
        instance.Description = validated_data.get('Description', instance.Description)
        instance.Release = validated_data.get('Release', instance.Release)
        instance.Is_Finished = validated_data.get('Is_Finished', instance.Is_Finished)
        instance.Chapters = validated_data.get('Chapters', instance.Chapters)
        instance.artist = validated_data.get('Artist', instance.artist)
        instance.Image = validated_data.get('Image', instance.Image)
        instance.ratingCount = validated_data.get('RatingCount', instance.ratingCount)
        instance.rating = validated_data.get('Rating', instance.rating)
        instance.Category = ','.join(categories)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_image', 'about','bookmarks','favourite']
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



class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    manga = serializers.ReadOnlyField(source='manga.Title')

    class Meta:
        model = Review
        fields = ['id', 'user', 'manga', 'text', 'rating', 'created_at']





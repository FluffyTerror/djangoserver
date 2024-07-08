from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from MangaLib.models import Manga, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_image', 'password')






class MangaSerializer(serializers.ModelSerializer):
    Category = serializers.ListField(
        child=serializers.CharField(max_length=64),
        source='get_categories',
        write_only=True
    )
    Category_display = serializers.CharField(source='Category', read_only=True)

    class Meta:
        model = Manga
        fields = ("Title", "Author", "Description", "Release", "Is_Finished", "Chapters", "Illustrator", "Category",
                  "Category_display")

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
        instance.Illustrator = validated_data.get('Illustrator', instance.Illustrator)
        instance.Category = ','.join(categories)
        instance.save()
        return instance



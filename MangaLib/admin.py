from django.contrib import admin

from .models import User, Manga, News, Review

# Register your models here.
admin.site.register(User)
admin.site.register(Manga)
admin.site.register(News)
admin.site.register(Review)
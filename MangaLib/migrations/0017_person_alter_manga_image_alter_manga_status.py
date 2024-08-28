# Generated by Django 5.0.6 on 2024-08-27 22:21

import MangaLib.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MangaLib', '0016_alter_manga_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_image', models.ImageField(default='Users/User profile picture.png', upload_to=MangaLib.models.user_profile_image_directory_path)),
                ('Nickname', models.CharField(max_length=128)),
                ('Country', models.CharField(max_length=32)),
                ('Type', models.CharField(choices=[('Автор', 'author'), ('Издатель', 'publisher'), ('Художник', 'artist')], max_length=32)),
                ('About', models.TextField(max_length=500)),
            ],
        ),
        migrations.AlterField(
            model_name='manga',
            name='Image',
            field=models.ImageField(default='Manga/image_10.png', upload_to='Manga/'),
        ),
        migrations.AlterField(
            model_name='manga',
            name='Status',
            field=models.CharField(choices=[('Завершён', 'completed'), ('Анонс', 'announced'), ('Приостановлен', 'paused'), ('Выпуск прекращён', 'discontinued'), ('Выходит', 'ongoing')], max_length=64),
        ),
    ]
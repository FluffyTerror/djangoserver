# Generated by Django 5.0.6 on 2024-08-18 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MangaLib', '0013_alter_manga_image_alter_user_profile_image_news'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='mangapage',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='mangapage',
            name='Chapter_Title',
            field=models.CharField(default='Chapter title', max_length=128),
        ),
        migrations.AlterUniqueTogether(
            name='mangapage',
            unique_together={('manga', 'volume', 'chapter', 'page_image', 'Chapter_Title')},
        ),
    ]
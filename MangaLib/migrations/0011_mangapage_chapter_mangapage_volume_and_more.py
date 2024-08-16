# Generated by Django 5.0.6 on 2024-08-15 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MangaLib', '0010_rename_is_finished_manga_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='mangapage',
            name='chapter',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='mangapage',
            name='volume',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterUniqueTogether(
            name='mangapage',
            unique_together={('manga', 'volume', 'chapter', 'page_image')},
        ),
    ]

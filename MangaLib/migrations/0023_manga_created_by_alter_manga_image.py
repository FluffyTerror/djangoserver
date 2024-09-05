# Generated by Django 5.0.6 on 2024-09-04 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MangaLib', '0022_manga_url_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='manga',
            name='Created_by',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='manga',
            name='Image',
            field=models.ImageField(default='Manga/image_10.jpg', upload_to='Manga/'),
        ),
    ]
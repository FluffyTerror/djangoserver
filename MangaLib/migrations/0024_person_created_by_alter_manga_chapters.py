# Generated by Django 5.0.6 on 2024-09-07 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MangaLib', '0023_manga_created_by_alter_manga_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='Created_by',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='manga',
            name='Chapters',
            field=models.IntegerField(default=0),
        ),
    ]
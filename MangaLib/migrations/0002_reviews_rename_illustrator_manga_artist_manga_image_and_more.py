# Generated by Django 5.0.6 on 2024-07-09 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MangaLib', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=1000)),
                ('rating', models.FloatField(default=0)),
                ('date_posted', models.DateField()),
                ('manga_title', models.CharField()),
            ],
        ),
        migrations.RenameField(
            model_name='manga',
            old_name='Illustrator',
            new_name='artist',
        ),
        migrations.AddField(
            model_name='manga',
            name='Image',
            field=models.ImageField(default='image 8.png', upload_to='media/manga'),
        ),
        migrations.AddField(
            model_name='manga',
            name='rating',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='manga',
            name='ratingCount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='about',
            field=models.CharField(default='Что-то обо мне...', max_length=500),
        ),
        migrations.AlterField(
            model_name='manga',
            name='Category',
            field=models.CharField(),
        ),
    ]

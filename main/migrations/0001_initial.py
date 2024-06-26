# Generated by Django 5.0.6 on 2024-05-23 21:59

import django.db.models.deletion
import django.utils.timezone
import mptt.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=30, verbose_name='Фамилия')),
                ('patronymic', models.CharField(blank=True, max_length=30, null=True, verbose_name='Отчество')),
            ],
            options={
                'verbose_name': 'Автор',
                'verbose_name_plural': 'Авторы',
                'ordering': ['last_name'],
                'unique_together': {('first_name', 'last_name')},
            },
        ),
        migrations.CreateModel(
            name='AuthorPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to='authors/', verbose_name='Фотография')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.author', verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Фотография автора',
                'verbose_name_plural': 'Фотографии авторов',
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, max_length=300, null=True, unique=True)),
                ('russian_title', models.CharField(max_length=300, verbose_name='Наименование книги на русском языке')),
                ('original_title', models.CharField(blank=True, max_length=300, null=True, verbose_name='Наименование книги на зыке оригинала')),
                ('publication_date', models.PositiveIntegerField(blank=True, help_text='ГГГГ', null=True, verbose_name='Год издания')),
                ('page_count', models.PositiveIntegerField(blank=True, null=True, verbose_name='Количество страниц')),
                ('instance_count', models.PositiveIntegerField(default=0, verbose_name='Количество экземпляров книги')),
                ('reader_count', models.PositiveIntegerField(default=0, verbose_name='Количество прочитавших')),
                ('rating', models.DecimalField(decimal_places=2, default=0, max_digits=3, verbose_name='Рейтинг')),
                ('author', models.ManyToManyField(to='main.author', verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Книга',
                'verbose_name_plural': 'Книги',
                'ordering': ['russian_title', 'instance_count'],
            },
        ),
        migrations.CreateModel(
            name='BookInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Стоимость')),
                ('price_per_day', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Цена за день использования')),
                ('registration_date', models.DateField(default=django.utils.timezone.now, verbose_name='Дата регистрации')),
                ('status', models.CharField(choices=[('available', 'доступна для выдачи'), ('not available', 'НЕ доступна для выдачи')], default='available', max_length=13, verbose_name='Статус')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.book', verbose_name='Книга')),
            ],
            options={
                'verbose_name': 'Экземпляр книги',
                'verbose_name_plural': 'Экземпляры книг',
            },
        ),
        migrations.CreateModel(
            name='BookPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to='book_covers/', verbose_name='Фотография обложки')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.book', verbose_name='Книга')),
            ],
            options={
                'verbose_name': 'Фотография книги',
                'verbose_name_plural': 'Фотографии книг',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Жанр')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='main.genre')),
            ],
            options={
                'verbose_name': 'Жанр',
                'verbose_name_plural': 'Жанры',
            },
        ),
        migrations.AddField(
            model_name='book',
            name='genre',
            field=mptt.fields.TreeManyToManyField(to='main.genre', verbose_name='Жанр'),
        ),
        migrations.AlterUniqueTogether(
            name='book',
            unique_together={('russian_title', 'original_title', 'publication_date', 'page_count')},
        ),
    ]

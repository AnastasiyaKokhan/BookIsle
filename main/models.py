from django.db import models
from django.urls import reverse
from slugify import slugify
from django.utils import timezone
from mptt.fields import TreeForeignKey, TreeManyToManyField
from mptt.models import MPTTModel


# Create your models here.


class Author(models.Model):
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=30, blank=True, null=True, verbose_name='Отчество')

    class Meta:
        unique_together = ['first_name', 'last_name']
        ordering = ['last_name',]
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    def __str__(self):
        return f'{self.first_name} {self.last_name} '


class AuthorPhoto(models.Model):
    author = models.ForeignKey('Author', on_delete=models.CASCADE, verbose_name='Автор')
    photo = models.ImageField(upload_to='authors/', verbose_name='Фотография')

    class Meta:
        verbose_name = 'Фотография автора'
        verbose_name_plural = 'Фотографии авторов'

    def __str__(self):
        return f'{self.author.last_name} {self.author.first_name}'


class Genre(MPTTModel):
    name = models.CharField(max_length=100, unique=True, verbose_name='Жанр')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Book(models.Model):
    slug = models.SlugField(max_length=300, unique=True, blank=True, null=True)
    author = models.ManyToManyField('Author', verbose_name='Автор')
    genre = TreeManyToManyField('Genre', verbose_name='Жанр')
    russian_title = models.CharField(max_length=300, verbose_name='Наименование книги на русском языке')
    original_title = models.CharField(max_length=300, blank=True, null=True,
                                      verbose_name='Наименование книги на зыке оригинала')
    publication_date = models.PositiveIntegerField(blank=True, null=True, verbose_name='Год издания', help_text="ГГГГ")
    page_count = models.PositiveIntegerField(blank=True, null=True, verbose_name='Количество страниц')
    instance_count = models.PositiveIntegerField(default=0, verbose_name='Количество экземпляров книги')
    reader_count = models.PositiveIntegerField(default=0, verbose_name='Количество прочитавших')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name='Рейтинг')

    class Meta:
        unique_together = ['russian_title', 'original_title', 'publication_date', 'page_count',]
        ordering = ['russian_title', '-instance_count']
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

    def __str__(self):
        return f'{self.russian_title}, {self.publication_date}'

    def save(self, *args, **kwargs):
        if self.original_title:
            self.slug = f'{slugify(self.original_title)}'
        else:
            self.slug = f'{slugify(self.russian_title)}'
        slug = self.slug
        suffix = 1
        while Book.objects.filter(slug=slug).exists():
            slug = f"{self.slug}-{suffix}"
            suffix += 1
        self.slug = slug
        return super(Book, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('book_description', kwargs={'book_slug': self.slug})

    def count_available_book_instances(self):
        return self.bookinstance_set.filter(status='available').count()


class BookInstance(models.Model):
    STATUS = {
        "available": "доступна для выдачи",
        "not_available": "НЕ доступна для выдачи",
    }
    book = models.ForeignKey('Book', on_delete=models.CASCADE, verbose_name='Книга')
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Стоимость')
    price_per_day = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Цена за день использования')
    registration_date = models.DateField(default=timezone.now, verbose_name='Дата регистрации')
    status = models.CharField(max_length=13, choices=STATUS, default='available', verbose_name='Статус')

    class Meta:
        verbose_name = 'Экземпляр книги'
        verbose_name_plural = 'Экземпляры книг'

    def __str__(self):
        return self.book.russian_title

    def save(self, *args, **kwargs):
        super(BookInstance, self).save(*args, **kwargs)
        book = self.book
        instance_count = BookInstance.objects.filter(book=book).count()
        book.instance_count = instance_count
        book.save()

    def delete(self, *args, **kwargs):
        book = self.book
        instance_count = BookInstance.objects.filter(book=book).count()
        book.instance_count = instance_count - 1
        book.save()
        super(BookInstance, self).delete(*args, **kwargs)


class BookPhoto(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, verbose_name='Книга')
    photo = models.ImageField(upload_to='book_covers/', verbose_name='Фотография обложки')

    class Meta:
        verbose_name = 'Фотография книги'
        verbose_name_plural = 'Фотографии книг'

    def __str__(self):
        return self.book.russian_title

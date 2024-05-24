from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter

from .models import Book, AuthorPhoto, Author, Genre, BookInstance, BookPhoto

# Register your models here.


class AuthorItemInline(admin.TabularInline):
    model = AuthorPhoto


class AuthorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name']
    inlines = [AuthorItemInline]


admin.site.register(Author, AuthorAdmin)

admin.site.register(AuthorPhoto)

admin.site.register(Genre, DraggableMPTTAdmin)


class BookItemInline(admin.TabularInline):
    model = BookPhoto


class BookAdmin(admin.ModelAdmin):
    list_display = ['russian_title', 'original_title', 'publication_date', 'page_count', 'instance_count']
    list_filter = (('genre', TreeRelatedFieldListFilter),)
    inlines = [BookItemInline]


admin.site.register(Book, BookAdmin)


class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'book', 'status']


admin.site.register(BookInstance, BookInstanceAdmin)


class BookPhotoAdmin(admin.ModelAdmin):
    list_display = ['book']


admin.site.register(BookPhoto, BookPhotoAdmin)

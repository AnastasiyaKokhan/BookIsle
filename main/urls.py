from django.urls import path

from .views import get_main_page, get_books_page, search_books_view, get_book_description_page, delete_book_instance, \
    get_add_book_page

urlpatterns = [
    path('', get_main_page, name='main'),
    path('books/', get_books_page, name='books'),
    path('book_search/', search_books_view, name='book_search'),
    path('book_description/<slug:book_slug>/', get_book_description_page, name='book_description'),
    path('delete_book_instance/<int:id>/', delete_book_instance, name='delete_book_instance'),
    path('add_book/', get_add_book_page, name='add_book'),
]

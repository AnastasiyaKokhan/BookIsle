from django.urls import path

from .views import get_main_page, get_books_page, get_book_description_page, get_add_book_page

urlpatterns = [
    path('', get_main_page),
    path('books/', get_books_page),
    path('book_description/', get_book_description_page),
    path('add_book/', get_add_book_page),
]

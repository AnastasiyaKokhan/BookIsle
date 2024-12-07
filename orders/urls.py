from django.urls import path

from .views import get_cart_page, add_to_cart, remove_from_cart, clear_cart, rent_books, get_order_page, return_books

urlpatterns = [
    path('', get_cart_page, name='cart'),
    path('add_to_cart/<int:bookinstance_id>/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:cartitem_id>/', remove_from_cart, name='remove_from_cart'),
    path('clear_cart/', clear_cart, name='clear_cart'),
    path('rent_books/', rent_books, name='rent_books'),
    path('order/<int:reader_id>/', get_order_page, name='order'),
    path('return_books/<int:reader_id>/', return_books, name='return_books'),
]

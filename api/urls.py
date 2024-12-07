from django.urls import path

from .views import search_readers

urlpatterns = [
    path('search_readers/', search_readers),
]


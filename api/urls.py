from django.urls import path

from .views import search_authors

urlpatterns = [
    path('search_authors/', search_authors),
]
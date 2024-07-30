from django.urls import path

from .views import get_sign_in_page, get_sign_up_page, sign_out

urlpatterns = [
    path('sign_in/', get_sign_in_page, name='sign_in'),
    path('sign_up/', get_sign_up_page, name='sign_up'),
    path('sign_out/', sign_out, name='sign_out'),
]

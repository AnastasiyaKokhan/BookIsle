from django.shortcuts import render

# Create your views here.


def get_main_page(request):
    return render(request, 'main.html')


def get_books_page(request):
    return render(request, 'books.html')


def get_book_description_page(request):
    return render(request, 'book_description.html')


def get_add_book_page(request):
    return render(request, 'add_book.html')

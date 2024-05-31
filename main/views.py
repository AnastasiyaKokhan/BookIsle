from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Book, Genre, Author, BookInstance


# Create your views here.


def get_main_page(request):
    all_instances = BookInstance.objects.count()
    all_not_available_instances = BookInstance.objects.filter(status='not_available').count()
    popular_books = Book.objects.all()[:3]

    context = {
        'all_instance_count': all_instances,
        'all_not_available_instance_count': all_not_available_instances,
        'popular_books': popular_books,
    }

    return render(request, 'main.html', context)


def get_books_page(request):
    books = Book.objects.all()
    genres = Genre.objects.all()

    paginator = Paginator(books, 20)
    if 'page' in request.GET:
        page_number = request.GET['page']
    else:
        page_number = 1
    page_books = paginator.get_page(page_number)

    context = {
        'books': books,
        'genres': genres,
        'page_books': page_books,
    }

    return render(request, 'books.html', context)


def search_books_view(request):
    books = Book.objects.all()
    genres = Genre.objects.all()

    search = request.POST.get('search')
    if request.method == 'POST':
        if request.POST.get('search'):
            if len(request.POST.get('search')) >= 3:
                search_results = []
                books_by_russian_title = Book.objects.filter(russian_title__icontains=search)
                books_by_original_title = Book.objects.filter(original_title__icontains=search)
                search_results.extend(books_by_russian_title)
                search_results.extend(books_by_original_title)
                authors_by_first_name = Author.objects.filter(first_name__icontains=search)
                for author in authors_by_first_name:
                    search_results.extend(author.book_set.all())
                authors_by_last_name = Author.objects.filter(last_name__icontains=search)
                for author in authors_by_last_name:
                    search_results.extend(author.book_set.all())
                books = search_results

    paginator = Paginator(books, 20, 1)
    if 'page' in request.GET:
        page_number = request.GET['page']
    else:
        page_number = 1
    page_books = paginator.get_page(page_number)

    context = {
        'books': books,
        'genres': genres,
        'search': search,
        'page_books': page_books,
    }

    return render(request, 'books.html', context)


def get_book_description_page(request):
    return render(request, 'book_description.html')


def get_add_book_page(request):
    return render(request, 'add_book.html')

from itertools import chain

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect

from .models import Book, Genre, Author, BookInstance


# Create your views here.


def get_main_page(request):
    all_instances = BookInstance.objects.count()
    all_not_available_instances = BookInstance.objects.filter(status='not_available').count()
    popular_books = Book.objects.all().order_by('page_count')[:3]

    context = {
        'all_instance_count': all_instances,
        'all_not_available_instance_count': all_not_available_instances,
        'popular_books': popular_books,
    }

    return render(request, 'main.html', context)


def get_books_page(request):
    books = Book.objects.all()
    genres = Genre.objects.all()

    if request.method == 'POST':
        get_parent = request.POST.getlist('parent')
        get_children = request.POST.getlist('child')
        if request.POST.get('parent'):
            checked_parent = genres.filter(id__in=get_parent)
            books_by_parent = Book.objects.filter(genre__in=checked_parent)
            books = books_by_parent
            if request.POST.get('child'):
                checked_children = genres.filter(id__in=get_children)
                books_by_children = Book.objects.filter(genre__in=checked_children).distinct()
                books = list(chain(books_by_parent, books_by_children))
        else:
            checked_children = genres.filter(id__in=get_children)
            books_by_children = Book.objects.filter(genre__in=checked_children).distinct()
            books = books_by_children

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
                books_by_title = Book.objects.filter(Q(russian_title__icontains=search) | Q(original_title__icontains=search))
                authors = Author.objects.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search))
                books_by_author = []
                for author in authors:
                    books_by_author = author.book_set.all()
                books = list(chain(books_by_title, books_by_author))

    paginator = Paginator(books, 20)
    if 'page' in request.GET:
        page_number = request.GET['page']
    else:
        page_number = 1
    page_books = paginator.get_page(page_number)

    context = {
        'genres': genres,
        'search': search,
        'page_books': page_books,
    }

    return render(request, 'books.html', context)


def get_book_description_page(request, book_slug):
    books = Book.objects.prefetch_related('bookphoto_set')
    book = books.get(slug=book_slug)

    instances = book.bookinstance_set.all()
    paginator = Paginator(instances, 20)
    if 'page' in request.GET:
        page_number = request.GET['page']
    else:
        page_number = 1
    page_instances = paginator.get_page(page_number)

    context = {
        'book': book,
        'page_instances': page_instances,
    }

    return render(request, 'book_description.html', context)


def delete_book_instance(request, id):
    book_instance = BookInstance.objects.get(id=id)
    slug = book_instance.book.slug
    book_instance.delete()
    return redirect('book_description', book_slug=slug)


def get_add_book_page(request):

    context = {

    }

    return render(request, 'add_book.html', context)

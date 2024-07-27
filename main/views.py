from itertools import chain

from django.contrib.postgres.search import SearchVector
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect

from .forms import BookInstanceForm
from .models import Book, Genre, Author, BookInstance, BookPhoto, AuthorPhoto


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
    errors = {}

    if request.method == 'POST':
        get_children = request.POST.getlist('child')
        if get_children:
            checked_children = genres.filter(id__in=get_children)
            books = Book.objects.filter(genre__in=checked_children).distinct()
        else:
            errors['filtration'] = '* выберите жанры'

    paginator = Paginator(books, 20)
    page_number = request.GET.get('page')
    try:
        page_books = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_books = paginator.page(1)
    except EmptyPage:
        page_books = paginator.page(paginator.num_pages)

    context = {
        'books': books,
        'genres': genres,
        'errors': errors,
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
                authors = (Author.objects
                           .annotate(search=SearchVector('first_name', 'last_name'))
                           .filter(Q(search=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)))
                books_by_author = []
                for author in authors:
                    books_by_author = author.book_set.all()
                books = list(chain(books_by_title, books_by_author))

    if request.method == 'POST':
        get_children = request.POST.getlist('child')
        if get_children:
            checked_children = genres.filter(id__in=get_children)
            books = Book.objects.filter(genre__in=checked_children).distinct()

    paginator = Paginator(books, 20)
    page_number = request.GET.get('page')
    try:
        page_books = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_books = paginator.page(1)
    except EmptyPage:
        page_books = paginator.page(paginator.num_pages)

    context = {
        'genres': genres,
        'search': search,
        'page_books': page_books,
    }

    return render(request, 'books.html', context)


def get_book_description_page(request, book_slug):
    books = Book.objects.prefetch_related('bookphoto_set')
    try:
        book = books.get(slug=book_slug)
    except ObjectDoesNotExist:
        return redirect('error')

    instances = book.bookinstance_set.all()
    paginator = Paginator(instances, 20)
    page_number = request.GET.get('page')
    try:
        page_instances = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_instances = paginator.page(1)
    except EmptyPage:
        page_instances = paginator.page(paginator.num_pages)

    book_photos = book.bookphoto_set.all()
    if not instances:
        book_photos.delete()
        book.delete()
        return redirect('books')

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
    genres = Genre.objects.all()
    errors = []

    context = {
        'genres': genres,
        'errors': errors,
    }

    if request.method == "POST":
        authors = []
        for author_index in range(10):
            first_name = request.POST.get(f'first_name_{author_index}')
            last_name = request.POST.get(f'last_name_{author_index}')
            patronymic = request.POST.get(f'patronymic_{author_index}')
            author_photos = request.FILES.getlist(f'photos_{author_index}')
            if first_name and last_name:
                new_author = Author.objects.filter(first_name=first_name, last_name=last_name)
                if new_author.exists():
                    authors.append(new_author)
                else:
                    new_author = Author(first_name=first_name, last_name=last_name, patronymic=patronymic)
                    new_author.save()
                    if author_photos:
                        for photo in author_photos:
                            author_photo_instance = AuthorPhoto(author=new_author, photo=photo)
                            author_photo_instance.save()
                            authors.append(new_author)
                    else:
                        errors.append("Добавьте фотографию автора.")
                        break
            elif last_name or first_name or patronymic:
                errors.append("Введите фамилию и имя автора.")
                if not author_photos:
                    errors.append("Добавьте фотографию автора.")
                break

        russian_title = request.POST.get('russian_title')
        original_title = request.POST.get('original_title')
        publication_date = request.POST.get('publication_date')
        page_count = request.POST.get('page_count')
        genre_ids = request.POST.getlist('child')
        price = request.POST.get('price')
        price_per_day = request.POST.get('price_per_day')
        instance_count = int(request.POST.get('instance_count'))

        new_book = Book.objects.filter(
            Q(russian_title=russian_title, publication_date=publication_date or None, page_count=page_count or None) |
            Q(original_title=original_title, publication_date=publication_date or None, page_count=page_count or None)
        )

        if genre_ids and russian_title and not new_book.exists():
            new_book = Book(russian_title=russian_title, original_title=original_title,
                            publication_date=publication_date or None, page_count=page_count or None)
            new_book.save()
            new_book.author.set(authors)
            new_book.genre.set(genre_ids)
            book_photos = request.FILES.getlist('book_photos')
            if book_photos:
                for photo in book_photos:
                    book_photo_instance = BookPhoto(book=new_book, photo=photo)
                    book_photo_instance.save()
                if price and price_per_day and instance_count:
                    for book_instance in range(instance_count):
                        new_book_instance = BookInstance(book=new_book, price=price, price_per_day=price_per_day)
                        new_book_instance.save()
                return redirect('books')
            else:
                errors.append("Добавьте фотографию обложки книги.")
        if new_book.exists():
            errors.append("Такая книга уже существует.")
        if not russian_title:
            errors.append("Введите наименование книги на русском языке.")
        if not genre_ids:
            errors.append("Выберите хотя бы один жанр.")
        if not price:
            errors.append("Введите стоимость.")
        if not price_per_day:
            errors.append("Введите цену за день использования.")
        if not instance_count:
            errors.append("Введите количество экземпляров.")

    return render(request, 'add_book.html', context)


def get_add_book_instance_page(request, book_slug):
    books = Book.objects.prefetch_related('bookphoto_set')
    try:
        book = books.get(slug=book_slug)
    except ObjectDoesNotExist:
        return redirect('error')
    form = BookInstanceForm()
    if request.method == "POST":
        form = BookInstanceForm(request.POST)
        if form.is_valid():
            price = form.cleaned_data.get('price')
            price_per_day = form.cleaned_data.get('price_per_day')
            instance_count = int(form.cleaned_data.get('instance_count'))
            for _ in range(instance_count):
                new_book_instance = BookInstance(book=book, price=price, price_per_day=price_per_day)
                new_book_instance.save()
            return redirect('book_description', book_slug=book_slug)
        else:
            form = BookInstanceForm(request.POST)

    context = {
        'form': form,
    }

    return render(request, 'add_book_instance.html', context)


def get_error_page(request):
    return render(request, 'error.html')

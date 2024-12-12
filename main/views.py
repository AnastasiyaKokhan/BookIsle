import calendar
from itertools import chain
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from django.shortcuts import render, redirect

from orders.models import Order, BookReturn
from orders.views import count_total_price
from .decorators import allowed_groups
from .forms import AddBookInstanceForm
from .models import Book, Genre, Author, BookInstance, BookPhoto, AuthorPhoto


# Create your views here.


def paginate_objects(request, object_list, objects_per_page):
    paginator = Paginator(object_list, objects_per_page)
    page_number = request.GET.get('page')
    try:
        page_objects = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_objects = paginator.page(1)
    except EmptyPage:
        page_objects = paginator.page(paginator.num_pages)
    return page_objects


def order_books(request, books):
    order = request.GET.get('o', 'russian_title')
    descending = order.startswith('-')
    sort_field = order[1:] if descending else order
    valid_sorting_fields = ['russian_title', 'count_available_book_instances']
    books = books.annotate(
        count_available_book_instances=Count('bookinstance', filter=Q(bookinstance__status='available'))
    )
    if sort_field in valid_sorting_fields:
        books = books.order_by(order)
    else:
        books = books.order_by('russian_title', '-count_available_book_instances')
    return books, order


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def get_main_page(request):
    all_instances = BookInstance.objects.count()
    all_not_available_instances = BookInstance.objects.filter(status='not_available').count()
    all_readers = User.objects.filter(groups__name='reader').count()
    popular_books = Book.objects.all().annotate(readers=Count('bookinstance__bookreturn')).order_by('-readers')[:3]

    this_year = datetime.now().year
    previous_year = this_year - 1
    is_leap_year = calendar.isleap(this_year)
    days_in_february = 29 if is_leap_year else 28
    winter_start = datetime(previous_year, 12, 1)
    winter_end = datetime(this_year, 2, days_in_february)
    spring_start = datetime(this_year, 3, 1)
    spring_end = datetime(this_year, 5, 31)
    summer_start = datetime(this_year, 6, 1)
    summer_end = datetime(this_year, 8, 31)
    autumn_start = datetime(this_year, 9, 1)
    autumn_end = datetime(this_year, 11, 30)
    year_start = datetime(this_year, 1, 1)
    year_end = datetime(this_year, 12, 31)

    def calculate_income(start_date, end_date):
        book_returns = BookReturn.objects.filter(return_date__range=[start_date, end_date])
        total_income = sum(book.book_instance_price for book in book_returns)
        return total_income

    winter_income = calculate_income(winter_start, winter_end)
    spring_income = calculate_income(spring_start, spring_end)
    summer_income = calculate_income(summer_start, summer_end)
    autumn_income = calculate_income(autumn_start, autumn_end)
    year_income = calculate_income(year_start, year_end)

    context = {
        'instance_count': all_instances,
        'not_available_instance_count': all_not_available_instances,
        'readers_count': all_readers,
        'popular_books': popular_books,
        'this_year': this_year,
        'previous_year': previous_year,
        'winter_income': winter_income,
        'spring_income': spring_income,
        'summer_income': summer_income,
        'autumn_income': autumn_income,
        'year_income': year_income,
    }

    return render(request, 'main.html', context)


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def get_books_page(request):
    books = Book.objects.all()
    genres = Genre.objects.all()

    selected_genres = request.POST.getlist('child') if request.method == 'POST' else request.GET.getlist('child')
    selected_genres = [genre for genre in selected_genres if genre.isdigit()]
    if selected_genres:
        checked_children = genres.filter(id__in=selected_genres)
        books = books.filter(genre__in=checked_children).distinct()

    books, order = order_books(request, books)

    page_books = paginate_objects(request, books, 20)

    context = {
        'books': books,
        'genres': genres,
        'page_books': page_books,
        'current_order': order,
        'selected_genres': selected_genres,
    }

    return render(request, 'books.html', context)


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def search_books_view(request):
    books = Book.objects.all()
    genres = Genre.objects.all()

    search = request.POST.get('search') if request.method == 'POST' else request.GET.get('search')
    # if request.method == 'POST':
        # if search and len(search) >= 3:
        #     books_by_title = Book.objects.filter(Q(russian_title__icontains=search) | Q(original_title__icontains=search))
        #     authors = (Author.objects
        #                .annotate(search=SearchVector('first_name', 'last_name'))
        #                .filter(Q(search=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)))
        #     books_by_author = []
        #     for author in authors:
        #         books_by_author.extend(author.book_set.all())
        #     books = books_by_title | books_by_author
    if search and len(search) >= 3:
        authors = (Author.objects
                   .annotate(search=SearchVector('first_name', 'last_name'))
                   .filter(Q(search=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)))
        books = Book.objects.filter(
            Q(russian_title__icontains=search) | Q(original_title__icontains=search) |
            Q(author__in=authors)
        ).distinct()

    selected_genres = request.POST.getlist('child') if request.method == 'POST' else request.GET.getlist('child')
    selected_genres = [genre for genre in selected_genres if genre.isdigit()]
    if selected_genres:
        checked_children = genres.filter(id__in=selected_genres)
        books = books.filter(genre__in=checked_children).distinct()

    books, order = order_books(request, books)

    page_books = paginate_objects(request, books, 20)

    context = {
        'genres': genres,
        'search': search,
        'page_books': page_books,
        'current_order': order,
        'selected_genres': selected_genres,
    }

    return render(request, 'books.html', context)


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def get_book_description_page(request, book_slug):
    books = Book.objects.prefetch_related('bookphoto_set')
    try:
        book = books.get(slug=book_slug)
    except ObjectDoesNotExist:
        return redirect('error')

    instances = book.bookinstance_set.all()
    page_instances = paginate_objects(request, instances, 20)

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


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def delete_book_instance(request, book_instance_id):
    book_instance = BookInstance.objects.get(id=book_instance_id)
    slug = book_instance.book.slug
    book_instance.delete()
    return redirect('book_description', book_slug=slug)


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def delete_book(request, book_id):
    book = Book.objects.get(id=book_id)
    book.delete()
    return redirect('books')


@login_required(login_url='sign_in')
@allowed_groups('librarian')
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


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def get_add_book_instance_page(request, book_slug):
    books = Book.objects.prefetch_related('bookphoto_set')
    try:
        book = books.get(slug=book_slug)
    except ObjectDoesNotExist:
        return redirect('error')
    add_book_instance_form = AddBookInstanceForm()
    if request.method == "POST":
        form = AddBookInstanceForm(request.POST)
        if form.is_valid():
            price = form.cleaned_data.get('price')
            price_per_day = form.cleaned_data.get('price_per_day')
            instance_count = int(form.cleaned_data.get('instance_count'))
            for _ in range(instance_count):
                new_book_instance = BookInstance(book=book, price=price, price_per_day=price_per_day)
                new_book_instance.save()
            return redirect('book_description', book_slug=book_slug)

    context = {
        'add_book_instance_form': add_book_instance_form,
    }

    return render(request, 'add_book_instance.html', context)


@login_required(login_url='sign_in')
@allowed_groups('reader')
def get_personal_account_page(request):
    reader = request.user
    try:
        order = Order.objects.get(reader=reader)
        order_items = order.orderitem_set.all()
        total_quantity = order_items.count()
        now = datetime.now()
        issue_date = datetime.combine(order.issue_date, datetime.min.time())
        period_of_use = now - issue_date
        total_price, sale, fine = count_total_price(order_items, period_of_use.days)

        context = {
            'order': order,
            'order_items': order_items,
            'total_quantity': total_quantity,
            'total_price': total_price,
            'fine': fine,
        }
    except ObjectDoesNotExist:
        context = {}

    return render(request, 'personal_account.html', context)


def get_error_page(request):
    return render(request, 'error.html')

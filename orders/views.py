from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from main.decorators import allowed_groups
from .forms import BookReturnForm
from django.forms.formsets import formset_factory
from .models import BookInstance, CartItem, OrderItem, Order, BookReturn, DamagePhoto


# Create your views here.


def count_total_price(books, days_of_use):
    total_price = 0
    total_quantity = books.count()
    sale = 0
    fine = 0
    for book in books:
        book_price = book.book_instance.price_per_day * days_of_use
        total_price += round(float(book_price), 2)
    if total_quantity > 4:
        sale = 15
        total_price *= 0.85
    elif total_quantity > 2:
        sale = 10
        total_price *= 0.9
    if days_of_use > 30:
        delay_period = days_of_use - 30
        fine = round((total_price * 0.01) * delay_period, 2)
        total_price += fine
    return round(total_price, 2), sale, fine


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def get_cart_page(request):
    cart_items = CartItem.objects.all()
    books_in_cart = []
    total_quantity = cart_items.count()
    errors = {}
    total_price, sale, fine = count_total_price(cart_items, 30)
    for item in cart_items:
        book = item.book_instance.book
        if book in books_in_cart:
            errors['duplicated_book'] = '* нельзя взять несколько экземпляров одной книги'
        books_in_cart.append(book)
    if total_quantity > 5:
        errors['too_many_books'] = '* читатель может взять не более 5 книг'

    context = {
        'cart_items': cart_items,
        'total_quantity': total_quantity,
        'total_price': total_price,
        'sale': sale,
        'errors': errors,
    }

    return render(request, 'cart.html', context)


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def add_to_cart(request, bookinstance_id):
    book_instance = BookInstance.objects.get(id=bookinstance_id)
    cart_item = CartItem(book_instance=book_instance)
    cart_item.save()
    return redirect('books')


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def remove_from_cart(request, cartitem_id):
    cart_item = CartItem.objects.get(id=cartitem_id)
    cart_item.delete()
    return redirect('cart')


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def clear_cart(request):
    cart_items = CartItem.objects.all()
    for item in cart_items:
        item.delete()
    return redirect('cart')


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def rent_books(request):
    errors = {}
    cart_items = CartItem.objects.all()
    total_quantity = cart_items.count()
    total_price, sale, fine = count_total_price(cart_items, 30)
    if request.method == 'POST':
        reader_id = request.POST.get('reader')
        if reader_id:
            reader = User.objects.get(id=reader_id)
            if not Order.objects.filter(reader=reader):
                order = Order(reader=reader)
                order.save()
                for item in cart_items:
                    order_item = OrderItem(book_instance=item.book_instance, order=order)
                    item.delete()
                    order_item.save()
                return redirect('cart')
            else:
                errors['reader_didn\'t_return_book'] = '* читатель не вернул все книги'
        else:
            errors['reader_not_selected'] = '* читатель не выбран'

    context = {
        'cart_items': cart_items,
        'total_quantity': total_quantity,
        'total_price': total_price,
        'errors': errors,
    }

    return render(request, 'rent_books.html', context)


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def get_order_page(request, reader_id):
    order = Order.objects.get(reader=reader_id)
    order_items = order.orderitem_set.all()
    total_quantity = order_items.count()

    now = datetime.today()
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

    return render(request, 'order.html', context)


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def return_books(request, reader_id):
    order = Order.objects.get(reader=reader_id)
    order_items = order.orderitem_set.all()

    now = datetime.now()
    issue_date = datetime.combine(order.issue_date, datetime.min.time())
    period_of_use = now - issue_date
    total_price, sale, fine = count_total_price(order_items, period_of_use.days)

    ReturnBooksFormSet = formset_factory(BookReturnForm, extra=order_items.count())
    return_books_formset = ReturnBooksFormSet()
    errors = []
    if request.method == "POST":
        return_books_formset = ReturnBooksFormSet(request.POST, request.FILES)
        if return_books_formset.is_valid():
            selected_book_instances = []
            reviews_to_save = []
            try:
                for index, form in enumerate(return_books_formset):
                    book_instance_id = request.POST.get(f'book_instance_{index}')
                    return_date = form.cleaned_data.get('return_date')
                    fine_for_damage = form.cleaned_data.get('fine_for_damage')
                    damage_description = form.cleaned_data.get('damage_description')
                    photo1 = request.FILES.get(f'form-{index}-photo1')
                    photo2 = request.FILES.get(f'form-{index}-photo2')
                    reader_assessment = form.cleaned_data.get('reader_assessment')
                    changed_rental_cost = form.cleaned_data.get('changed_rental_cost')
                    if book_instance_id not in selected_book_instances:
                        selected_book_instances.append(book_instance_id)
                        book_instance = BookInstance.objects.get(id=book_instance_id)
                        price_per_day = book_instance.price_per_day
                        book_price = float(price_per_day * period_of_use.days)
                        if fine_for_damage:
                            book_price += float(fine_for_damage)
                            total_price += float(fine_for_damage)
                        if sale:
                            book_price = (book_price * (100 - sale)) / 100
                        if fine:
                            delay_period = period_of_use.days - 30
                            book_fine = (book_price * 0.01) * delay_period
                            book_price += book_fine
                        book_price = round(book_price, 2)
                        review = BookReturn(book_instance=book_instance, return_date=return_date,
                                            reader_assessment=reader_assessment, damage_description=damage_description,
                                            book_instance_price=book_price)
                        reviews_to_save.append((review, photo1, photo2, book_instance_id, changed_rental_cost))
                    else:
                        errors.append(f"Книга с ID {book_instance_id} уже была возвращена. Убедитесь, что вы не возвращаете один и тот же экземпляр несколько раз.")
                if not errors:
                    for review, photo1, photo2, book_instance_id, changed_rental_cost in reviews_to_save:
                        review.save()
                        if photo1:
                            DamagePhoto(book_damage=review, photo=photo1).save()
                        if photo2:
                            DamagePhoto(book_damage=review, photo=photo2).save()
                        if changed_rental_cost:
                            BookInstance.objects.filter(id=book_instance_id).update(price_per_day=changed_rental_cost)
                    order.delete()
                    return render(request, 'created.html',
                                  {'total_price': total_price, 'sale': sale, 'fine': fine})
            except ValueError:
                errors.append("Возврат был оформлен не для всех книг.")
            except BookInstance.DoesNotExist:
                errors.append(f"Книга с ID {book_instance_id} не найдена.")

    context = {
       'return_books_formset': return_books_formset,
       'order_items': order_items,
       'errors': errors,
    }

    return render(request, 'return_books.html', context)

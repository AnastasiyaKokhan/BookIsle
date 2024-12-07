from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.postgres.search import SearchVector
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, redirect

from config import settings
from main.decorators import allowed_groups
from main.views import paginate_objects
from .forms import SignInForm, SignUpForm
from .models import Profile


# Create your views here.


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def get_sign_up_page(request):
    sign_up_form = SignUpForm()
    if request.method == 'POST':
        sign_up_form = SignUpForm(request.POST)
        if sign_up_form.is_valid():
            cd = sign_up_form.cleaned_data
            first_name = cd['first_name']
            last_name = cd['last_name']
            email = cd['email']
            username = f"{first_name}_{last_name}"
            if User.objects.filter(username=username).exists():
                username = f"{username}_{User.objects.filter(username=username).count() + 1}"
            password = User.objects.make_random_password(length=10)
            patronymic = cd['patronymic']
            passport_number = cd['passport_number']
            birth = cd['birth_date']
            address = cd['residential_address']
            is_agreed = cd['is_agreed']
            new_user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                                email=email, password=password)
            Profile.objects.create(user=new_user, patronymic=patronymic, passport_number=passport_number,
                                   birth_date=birth, residential_address=address, is_agreed=is_agreed)
            new_user.save()

            reader_group = Group.objects.get(name='reader')
            new_user.groups.add(reader_group)

            subject = 'Информация для входа в личный кабинет'
            message = f'Имя пользователя: {username}. Пароль для входа в личный кабинет: {password}.'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            return redirect('readers')

    context = {
        'sign_up_form': sign_up_form
    }

    return render(request, 'sign_up.html', context)


def get_sign_in_page(request):
    sign_in_form = SignInForm()
    if request.method == 'POST':
        sign_in_form = SignInForm(request.POST)
        if sign_in_form.is_valid():
            cd = sign_in_form.cleaned_data
            username = cd['username']
            password = cd['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                if user.groups.filter(name='librarian').exists() or user.is_superuser == True:
                    return redirect('main')
                elif user.groups.filter(name='reader').exists():
                    return redirect('personal_account')

    context = {
        'sign_in_form': sign_in_form,
    }

    return render(request, 'sign_in.html', context)


def sign_out(request):
    logout(request)
    return redirect('main')


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def get_readers_page(request):
    readers = User.objects.filter(groups__name='reader')
    page_readers = paginate_objects(request, readers, 20)

    context = {
        'readers': readers,
        'page_readers': page_readers,
    }

    return render(request, 'readers.html', context)


@login_required(login_url='sign_in')
@allowed_groups('librarian')
def search_readers_view(request):
    readers = User.objects.filter(groups__name='reader')

    search = request.POST.get('search')
    if request.method == 'POST':
        if search and len(search) >= 3:
            readers = (User.objects.filter(groups__name='reader')
                       .annotate(search=SearchVector('first_name', 'last_name'))
                       .filter(Q(search=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)))

    page_readers = paginate_objects(request, readers, 20)

    context = {
        'search': search,
        'page_readers': page_readers,
    }

    return render(request, 'readers.html', context)

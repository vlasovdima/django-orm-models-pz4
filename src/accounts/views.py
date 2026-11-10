from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Course


def home(request):
    """Главная страница учебного проекта django_auth."""
    return render(request, 'home.html')


@login_required
def profile(request):
    """Защищенная страница профиля пользователя."""
    return render(request, 'profile.html')


@login_required
def course_list(request):
    """Страница со списком курсов и связанных факультетов (select_related)."""
    courses = Course.objects.select_related('department').all()

    return render(
        request,
        'course_list.html',
        {
            'courses': courses,
        }
    )

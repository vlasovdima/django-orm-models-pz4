"""
Скрипт наполнения базы данных начальными данными (п. 10–12 и 43)
и последовательного выполнения всех операций Django ORM (п. 15–34, 39)
с сохранением подробного протокола выполнения.
"""

import os
import sys

DJANGO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "django_auth"))
if DJANGO_DIR not in sys.path:
    sys.path.insert(0, DJANGO_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.contrib.auth.models import User
from accounts.models import Course, Department, StudentProfile


def seed_initial_admin_data():
    """Выполняет создание объектов, указанных в п. 10–12 и 43 методички."""
    # Очистка существующих записей для идемпотентности
    StudentProfile.objects.all().delete()
    Course.objects.all().delete()
    Department.objects.all().delete()

    # Убеждаемся, что пользователи admin и student1 существуют
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "Admin123!")
    student1, created = User.objects.get_or_create(username="student1")
    if created:
        student1.set_password("Student123!")
        student1.is_staff = False
        student1.is_superuser = False
        student1.save()

    # Пункт 10: Добавьте факультеты
    dep_it = Department.objects.create(name="Информационные технологии")
    dep_pm = Department.objects.create(name="Прикладная математика")

    # Пункт 11 и 43: Добавьте курсы и заполните описание (Description)
    c_web = Course.objects.create(
        title="Веб-программирование",
        department=dep_it,
        description="Разработка серверных веб-приложений на языке Python с использованием фреймворка Django."
    )
    c_db = Course.objects.create(
        title="Базы данных",
        department=dep_it,
        description="Проектирование реляционных баз данных, язык запросов SQL, нормализация и транзакции."
    )
    c_py = Course.objects.create(
        title="Программирование на Python",
        department=dep_it,
        description="Базовые конструкции языка Python, объектно-ориентированное программирование и работа с пакетами."
    )
    c_math = Course.objects.create(
        title="Математическое моделирование",
        department=dep_pm,
        description="Построение аналитических и численных моделей сложных технических и экономических систем."
    )

    # Пункт 12: Создайте профиль существующего пользователя student1
    profile = StudentProfile.objects.create(
        user=student1,
        department=dep_it
    )
    profile.courses.add(c_web, c_db, c_py)

    return dep_it, dep_pm, student1


def run_orm_walkthrough():
    """Пошагово выполняет команды ORM из пунктов 16–34 и 39 методички и формирует лог."""
    seed_initial_admin_data()

    lines = []
    def log_cmd(step_title, cmd_str, result_str):
        lines.append(f"# {step_title}")
        lines.append(f">>> {cmd_str}")
        if result_str is not None:
            lines.append(str(result_str))
        lines.append("")

    # Пункт 16: Импорт моделей
    log_cmd(
        "Пункт 16. Импорт моделей",
        "from accounts.models import Department, Course, StudentProfile\n>>> from django.contrib.auth.models import User",
        None
    )

    # Пункт 17: Получите все факультеты
    res_17 = repr(Department.objects.all())
    log_cmd("Пункт 17. Получение всех факультетов", "Department.objects.all()", res_17)

    # Пункт 18: Создайте объект через ORM
    dep = Department.objects.create(name='Автоматизация')
    log_cmd(
        "Пункт 18. Создание объекта через ORM",
        "dep = Department.objects.create(name='Автоматизация')\n>>> dep",
        repr(dep)
    )

    # Пункт 19: Получите объект по условию
    res_19_name = repr(Department.objects.get(name='Автоматизация'))
    first_dep_id = Department.objects.order_by('id').first().id
    res_19_id = repr(Department.objects.get(id=first_dep_id))
    log_cmd(
        "Пункт 19. Получение объекта по условию (get)",
        f"Department.objects.get(name='Автоматизация')\n{res_19_name}\n>>> Department.objects.get(id={first_dep_id})",
        res_19_id
    )

    # Пункт 20: Используйте filter
    res_20 = repr(Department.objects.filter(name__icontains='матем'))
    log_cmd(
        "Пункт 20. Фильтрация объектов без учёта регистра (icontains)",
        "Department.objects.filter(name__icontains='матем')",
        res_20
    )

    # Пункт 21: Создайте курс через ORM
    dep_it = Department.objects.get(name='Информационные технологии')
    course_new = Course.objects.create(
        title='Разработка веб-приложений',
        department=dep_it,
        description='Практический курс по архитектуре современных клиент-серверных систем и ORM.'
    )
    log_cmd(
        "Пункт 21. Создание курса через ORM",
        "dep = Department.objects.get(name='Информационные технологии')\n>>> course = Course.objects.create(title='Разработка веб-приложений', department=dep)\n>>> course",
        repr(course_new)
    )

    # Пункт 22: Получите все курсы факультета через related_name='courses'
    res_22 = repr(dep_it.courses.all())
    log_cmd(
        "Пункт 22. Получение курсов факультета в обратном направлении (related_name='courses')",
        "dep.courses.all()",
        res_22
    )

    # Пункт 23: Получите курсы через обычный фильтр
    res_23 = repr(Course.objects.filter(department=dep_it))
    log_cmd(
        "Пункт 23. Получение курсов через обычный фильтр Course.objects.filter",
        "Course.objects.filter(department=dep)",
        res_23
    )

    # Пункт 24: Получите пользователя
    user = User.objects.get(username='student1')
    log_cmd(
        "Пункт 24. Получение пользователя student1",
        "user = User.objects.get(username='student1')\n>>> user",
        repr(user)
    )

    # Пункт 25: Получите профиль пользователя
    profile = StudentProfile.objects.get(user=user)
    profile_rel = user.student_profile
    log_cmd(
        "Пункт 25. Получение профиля студента (через get и через OneToOne related_name)",
        f"profile = StudentProfile.objects.get(user=user)\n>>> profile\n{repr(profile)}\n>>> user.student_profile",
        repr(profile_rel)
    )

    # Пункт 26: Посмотрите факультет студента
    log_cmd(
        "Пункт 26. Просмотр факультета студента",
        "profile.department",
        repr(profile.department)
    )

    # Пункт 27: Посмотрите курсы студента
    log_cmd(
        "Пункт 27. Просмотр курсов студента",
        "profile.courses.all()",
        repr(profile.courses.all())
    )

    # Пункт 28: Добавьте студенту новый курс
    course_web_app = Course.objects.get(title='Разработка веб-приложений')
    profile.courses.add(course_web_app)
    log_cmd(
        "Пункт 28. Добавление студенту нового курса (ManyToMany add)",
        "course = Course.objects.get(title='Разработка веб-приложений')\n>>> profile.courses.add(course)\n>>> profile.courses.all()",
        repr(profile.courses.all())
    )

    # Пункт 29: Удалите курс у студента
    profile.courses.remove(course_web_app)
    log_cmd(
        "Пункт 29. Удаление курса у студента (ManyToMany remove)",
        "profile.courses.remove(course)\n>>> profile.courses.all()",
        repr(profile.courses.all())
    )

    # Пункт 30: Измените объект
    dep_auto = Department.objects.get(name='Автоматизация')
    dep_auto.name = 'Автоматизация и управление'
    dep_auto.save()
    log_cmd(
        "Пункт 30. Изменение объекта и сохранение в БД (save)",
        "dep = Department.objects.get(name='Автоматизация')\n>>> dep.name = 'Автоматизация и управление'\n>>> dep.save()\n>>> Department.objects.all()",
        repr(Department.objects.all())
    )

    # Пункт 31: Удалите объект
    del_result = dep_auto.delete()
    log_cmd(
        "Пункт 31. Удаление объекта из базы данных (delete)",
        "dep.delete()\n" + repr(del_result) + "\n>>> Department.objects.all()",
        repr(Department.objects.all())
    )

    # Пункт 32: Выполните выборку по связанной модели
    res_32 = repr(Course.objects.filter(department__name__icontains='Информационные'))
    log_cmd(
        "Пункт 32. Выборка по связанной модели через двойное подчёркивание (department__name__icontains)",
        "Course.objects.filter(department__name__icontains='Информационные')",
        res_32
    )

    # Пункт 33: Найдите студентов определённого курса
    course_vp = Course.objects.get(title='Веб-программирование')
    res_33 = repr(course_vp.students.all())
    log_cmd(
        "Пункт 33. Поиск студентов определённого курса (related_name='students')",
        "course = Course.objects.get(title='Веб-программирование')\n>>> course.students.all()",
        res_33
    )

    # Пункт 39: Посмотрите SQL-запрос ORM
    queryset = Course.objects.filter(department__name__icontains='Информационные')
    sql_str = str(queryset.query)
    log_cmd(
        "Пункт 39. Просмотр автоматически сгенерированного SQL-запроса (queryset.query)",
        "queryset = Course.objects.filter(department__name__icontains='Информационные')\n>>> print(queryset.query)",
        sql_str
    )

    output_text = "\n".join(lines)
    log_file = os.path.join(os.path.dirname(__file__), "orm_session_output.txt")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(output_text)

    print("[ORM Session] Все команды пунктов 16–39 успешно выполнены!")
    return output_text, sql_str


if __name__ == "__main__":
    out, sql = run_orm_walkthrough()
    print(out)

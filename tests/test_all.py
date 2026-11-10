"""
Комплексный набор автономных тестов для проверки ПЗ 4:
«Модели Django, ORM, миграции и административная панель».
Проверяет:
1. Синтаксическую компиляцию всех модулей Python.
2. Наличие всех файлов проекта согласно пункту 44 методички (включая миграции 0001 и 0002, course_list.html).
3. Наличие и корректность регистрации моделей Department, Course, StudentProfile в Django Admin.
4. Создание, чтение, обновление и удаление объектов через ORM (create, all, get, filter, save, delete).
5. Работу трёх типов связей:
   - User 1 : 1 StudentProfile (user.student_profile)
   - Department 1 : N Course (department.courses.all())
   - StudentProfile N : M Course (profile.courses.all(), course.students.all())
6. Выборку по связанной модели через двойное подчёркивание (department__name__icontains).
7. Автоматическую генерацию SQL-запроса (queryset.query с INNER JOIN).
8. Защиту маршрута /courses/ декоратором @login_required (аноним -> 302 Redirect на /accounts/login/?next=/courses/).
9. Отображение списка курсов и факультетов на странице /courses/ для авторизованного пользователя student1.
10. Работу административной панели (/admin/accounts/department/, /admin/accounts/course/, /admin/accounts/studentprofile/) под суперпользователем admin.
"""

import os
import sys
import unittest

DJANGO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "django_auth"))
if DJANGO_DIR not in sys.path:
    sys.path.insert(0, DJANGO_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.contrib import admin
from django.contrib.auth.models import User
from django.test import Client

from accounts.models import Course, Department, StudentProfile


class DjangoPZ4FullTestSuite(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_01_syntax_compilation(self):
        """Проверка синтаксиса всех файлов Python."""
        py_files = [
            os.path.join(DJANGO_DIR, "manage.py"),
            os.path.join(DJANGO_DIR, "config", "settings.py"),
            os.path.join(DJANGO_DIR, "config", "urls.py"),
            os.path.join(DJANGO_DIR, "accounts", "models.py"),
            os.path.join(DJANGO_DIR, "accounts", "admin.py"),
            os.path.join(DJANGO_DIR, "accounts", "views.py"),
            os.path.join(DJANGO_DIR, "accounts", "urls.py"),
            os.path.join(DJANGO_DIR, "accounts", "migrations", "0001_initial.py"),
            os.path.join(DJANGO_DIR, "accounts", "migrations", "0002_course_description.py"),
        ]
        for f in py_files:
            with self.subTest(file=f):
                self.assertTrue(os.path.exists(f), f"Файл не найден: {f}")
                with open(f, "r", encoding="utf-8") as fp:
                    code = fp.read()
                compiled = compile(code, f, "exec")
                self.assertIsNotNone(compiled)

    def test_02_structure_integrity_pz4(self):
        """Проверка структуры проекта согласно п. 44 методички."""
        expected_paths = [
            os.path.join(DJANGO_DIR, "manage.py"),
            os.path.join(DJANGO_DIR, "db.sqlite3"),
            os.path.join(DJANGO_DIR, "accounts", "migrations", "0001_initial.py"),
            os.path.join(DJANGO_DIR, "accounts", "migrations", "0002_course_description.py"),
            os.path.join(DJANGO_DIR, "accounts", "admin.py"),
            os.path.join(DJANGO_DIR, "accounts", "models.py"),
            os.path.join(DJANGO_DIR, "accounts", "urls.py"),
            os.path.join(DJANGO_DIR, "accounts", "views.py"),
            os.path.join(DJANGO_DIR, "config", "settings.py"),
            os.path.join(DJANGO_DIR, "config", "urls.py"),
            os.path.join(DJANGO_DIR, "templates", "registration", "login.html"),
            os.path.join(DJANGO_DIR, "templates", "profile.html"),
            os.path.join(DJANGO_DIR, "templates", "course_list.html"),
        ]
        for p in expected_paths:
            with self.subTest(path=p):
                self.assertTrue(os.path.exists(p), f"Отсутствует обязательный файл проекта: {p}")

    def test_03_admin_registration_and_customization(self):
        """Проверка регистрации моделей и настроек ModelAdmin (п. 8, 13)."""
        self.assertIn(Department, admin.site._registry)
        self.assertIn(Course, admin.site._registry)
        self.assertIn(StudentProfile, admin.site._registry)

        dep_admin = admin.site._registry[Department]
        self.assertEqual(dep_admin.list_display, ('id', 'name'))
        self.assertEqual(dep_admin.search_fields, ('name',))

        course_admin = admin.site._registry[Course]
        self.assertEqual(course_admin.list_display, ('id', 'title', 'department'))
        self.assertEqual(course_admin.list_filter, ('department',))
        self.assertEqual(course_admin.search_fields, ('title',))

        prof_admin = admin.site._registry[StudentProfile]
        self.assertEqual(prof_admin.list_display, ('id', 'user', 'department'))
        self.assertEqual(prof_admin.list_filter, ('department',))
        self.assertEqual(prof_admin.search_fields, ('user__username',))
        self.assertEqual(prof_admin.filter_horizontal, ('courses',))

    def test_04_orm_crud_operations(self):
        """Проверка базовых операций ORM: create, get, filter, save, delete (п. 17–20, 30–31)."""
        temp_dep = Department.objects.create(name="Автоматизация")
        fetched = Department.objects.get(name="Автоматизация")
        self.assertEqual(fetched.id, temp_dep.id)

        filtered = Department.objects.filter(name__icontains="матем")
        self.assertTrue(filtered.exists())
        self.assertEqual(filtered.first().name, "Прикладная математика")

        temp_dep.name = "Автоматизация и управление"
        temp_dep.save()
        self.assertEqual(Department.objects.get(id=temp_dep.id).name, "Автоматизация и управление")

        temp_dep.delete()
        self.assertFalse(Department.objects.filter(id=fetched.id).exists())

    def test_05_orm_relationships_1to1_1toN_NtoM(self):
        """Проверка трёх типов связей: 1:1, 1:N, N:M и обратных связей related_name (п. 21–29, 33)."""
        dep_it = Department.objects.get(name="Информационные технологии")
        user_st = User.objects.get(username="student1")

        # 1 : 1 (User <-> StudentProfile)
        profile = user_st.student_profile
        self.assertEqual(profile.user, user_st)
        self.assertEqual(profile.department, dep_it)

        # 1 : N (Department <-> Course)
        it_courses = dep_it.courses.all()
        self.assertGreaterEqual(it_courses.count(), 3)

        # N : M (StudentProfile <-> Course)
        course_web = Course.objects.get(title="Веб-программирование")
        self.assertIn(course_web, profile.courses.all())
        self.assertIn(profile, course_web.students.all())

    def test_06_orm_related_lookup_and_sql_query(self):
        """Проверка выборки по связанной модели и генерации SQL-запроса (п. 32, 39)."""
        qs = Course.objects.filter(department__name__icontains="Информационные")
        self.assertGreaterEqual(qs.count(), 3)
        sql = str(qs.query)
        self.assertIn("INNER JOIN", sql.upper())
        self.assertIn("accounts_department", sql)

    def test_07_courses_page_requires_login(self):
        """Неавторизованный запрос к /courses/ перенаправляется на /accounts/login/?next=/courses/ (п. 35, 38)."""
        response = self.client.get("/courses/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/?next=/courses/", response.headers.get("Location", ""))

    def test_08_courses_page_authorized_renders_courses(self):
        """Авторизованный пользователь student1 видит список курсов и факультетов на /courses/ (п. 35–38)."""
        self.client.login(username="student1", password="Student123!")
        response = self.client.get("/courses/")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        self.assertIn("Список курсов", html)
        self.assertIn("Веб-программирование", html)
        self.assertIn("Информационные технологии", html)
        self.assertIn("Математическое моделирование", html)
        self.assertIn("Прикладная математика", html)

    def test_09_course_description_field_populated(self):
        """Проверка поля description, добавленного во второй миграции (п. 40–43)."""
        course_web = Course.objects.get(title="Веб-программирование")
        self.assertTrue(bool(course_web.description.strip()))

    def test_10_admin_pages_accessible_by_superuser(self):
        """Суперпользователь admin успешно открывает разделы моделей в админ-панели (п. 9–14, 43)."""
        self.client.login(username="admin", password="Admin123!")
        urls = [
            "/admin/",
            "/admin/accounts/department/",
            "/admin/accounts/course/",
            "/admin/accounts/studentprofile/",
        ]
        for u in urls:
            with self.subTest(url=u):
                resp = self.client.get(u)
                self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)

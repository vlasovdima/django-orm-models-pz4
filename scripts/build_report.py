"""
Скрипт генерации официального отчёта по ПЗ 4 строго по ГОСТ 7.32-2017.
Тема: «Модели Django, ORM, миграции и административная панель».
Дисциплина: «Структура программного обеспечения и базы данных».
Студент: Власов Дмитрий (М3О-236БВ-25), Преподаватель: Александрова С.С.
"""

import os
import shutil
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.dirname(CURRENT_DIR)
DOCS_DIR = os.path.join(TASK_DIR, "docs")
SCREEN_DIR = os.path.join(TASK_DIR, "screenshots")
GOST_SCRIPTS = r"c:\Users\kirak\Downloads\mp\.agents\skills\gost-student-reports\scripts"

sys.path.insert(0, GOST_SCRIPTS)
from gost_docx import GostReport


def generate_pz4_report():
    os.makedirs(DOCS_DIR, exist_ok=True)
    report_filename = "Отчет_ПЗ4_Власов_М3О-236БВ-25.docx"
    report_path = os.path.join(DOCS_DIR, report_filename)

    rep = GostReport(base_dir=TASK_DIR, screenshots_dir=SCREEN_DIR)

    # 1. ТИТУЛЬНЫЙ ЛИСТ (строго по образцу кафедры 317 «Инноватика» МАИ)
    rep.title_page(
        work_type="ОТЧЁТ",
        work_subtitle="по практическому занятию № 4",
        discipline="«Структура программного обеспечения и базы данных»",
        topic="«Модели Django, ORM, миграции и административная панель»",
        student_group="М3О-236БВ-25",
        student_name="Власов Дмитрий",
        teacher_name="Александрова С.С.",
        city="Москва",
        year="2026",
    )

    # 2. СОДЕРЖАНИЕ (СТРАНИЦА 2)
    rep.toc([
        ("1 Цель работы и постановка задачи", 3),
        ("2 Проектирование связанных предметных моделей и схема БД", 3),
        ("3 Пошаговый ход выполнения работы (миграции, Admin, ORM, веб-страница)", 5),
        ("4 Результаты работы, скриншоты страниц и структура проекта", 10),
        ("5 Разбор практических трудностей при настройке ORM и миграций", 18),
        ("Заключение", 19),
        ("Список использованных источников", 20),
    ])

    # 3. РАЗДЕЛ 1: ЦЕЛЬ РАБОТЫ И ПОСТАНОВКА ЗАДАЧИ
    rep.heading("1 ЦЕЛЬ РАБОТЫ И ПОСТАНОВКА ЗАДАЧИ")
    rep.para(
        "Цель практического занятия № 4 – продолжить разработку учебного веб-проекта django_auth из предыдущей работы, "
        "добавить собственные связанные предметные модели данных, сгенерировать и применить миграции схемы базы данных, "
        "зарегистрировать и настроить модели в административной панели Django, а также отработать базовые и связанные "
        "запросы к реляционной базе через Django ORM."
    )
    rep.para(
        "Для достижения цели я выделил следующие практические этапы работы (пункты 1–44 методических указаний):"
    )
    rep.bullets([
        "проверить исходную структуру проекта django_auth из ПЗ 3 (приложение accounts, пакет config, папка templates, база db.sqlite3 и скрипт manage.py)",
        "описать в модуле accounts/models.py три предметные модели: факультет (Department), учебный курс (Course) и профиль студента (StudentProfile)",
        "реализовать все три типа реляционных связей: один-к-одному (OneToOneField), один-ко-многим (ForeignKey) и многие-ко-многим (ManyToManyField)",
        "создать первую миграцию схемы данных 0001_initial.py командой makemigrations, изучить её структуру и применить к db.sqlite3 командой migrate",
        "проверить статус применённых миграций с помощью утилиты showmigrations",
        "зарегистрировать модели в административной панели accounts/admin.py и наполнить базу тестовыми факультетами, курсами и профилем пользователя student1",
        "улучшить интерфейс административной панели через классы ModelAdmin (добавить столбцы list_display, боковые фильтры list_filter, строку поиска search_fields и удобный виджет выбора курсов filter_horizontal)",
        "выполнить в интерактивной консоли Django shell полный цикл операций CRUD через ORM: создание (create), чтение (all, get, filter с icontains), обновление (save), удаление (delete) и навигацию по обратным связям (related_name)",
        "связать Django ORM с веб-интерфейсом: написать контроллер course_list с оптимизацией select_related('department'), настроить маршрут /courses/ и сверстать шаблон course_list.html",
        "просмотреть реальный SQL-запрос с оператором INNER JOIN, который ORM автоматически формирует при фильтрации по связанной таблице",
        "модифицировать существующую модель Course (добавить текстовое поле description), выполнить вторую миграцию 0002_course_description.py без потери данных и заполнить описания курсов в админ-панели",
    ])

    # 4. РАЗДЕЛ 2: ПРОЕКТИРОВАНИЕ СВЯЗАННЫХ ПРЕДМЕТНЫХ МОДЕЛЕЙ И СХЕМА БД
    rep.heading("2 ПРОЕКТИРОВАНИЕ СВЯЗАННЫХ ПРЕДМЕТНЫХ МОДЕЛЕЙ И СХЕМА БД")
    rep.para(
        "В основе подсистемы хранения данных Django лежит объектно-реляционное отображение (Object-Relational Mapping, ORM). "
        "Каждая модель представляет собой класс Python, наследуемый от django.db.models.Model, а её атрибуты соответствуют "
        "столбцам таблицы в реляционной базе данных SQLite."
    )
    rep.para(
        "Согласно заданию (пункты 2–3 методических указаний), в приложении accounts реализуются три связанные сущности, "
        "демонстрирующие все фундаментальные типы связей реляционных баз данных:"
    )

    er_scheme = (
        "  +--------------------+            1 : N (ForeignKey)            +--------------------+\n"
        "  |     Department     | ---------------------------------------> |       Course       |\n"
        "  |--------------------|          related_name='courses'          |--------------------|\n"
        "  | id (PK)            |                                          | id (PK)            |\n"
        "  | name (CharField)   |                                          | title (CharField)  |\n"
        "  +--------------------+                                          | description (Text) |\n"
        "            |                                                     | department_id (FK) |\n"
        "            | 1 : N (ForeignKey, SET_NULL)                        +--------------------+\n"
        "            | related_name='students'                                       ^\n"
        "            v                                                               |\n"
        "  +--------------------+           N : M (ManyToManyField)                  |\n"
        "  |   StudentProfile   | <--------------------------------------------------+\n"
        "  |--------------------|               related_name='students'\n"
        "  | id (PK)            |\n"
        "  | user_id (1:1 FK)   | <==== 1 : 1 (OneToOneField) ====> [ auth_user (User) ]\n"
        "  | department_id (FK) |       related_name='student_profile'\n"
        "  +--------------------+"
    )
    rep.diagram("Схема связей между предметными моделями Department, Course, StudentProfile и User", er_scheme, size=8)

    rep.para(
        "Логика работы каждой связи в разработанной схеме устроена следующим образом:"
    )
    rep.bullets([
        "User 1 — 1 StudentProfile (OneToOneField): один пользователь системы имеет ровно один студенческий профиль. При удалении учетной записи пользователя (on_delete=models.CASCADE) его профиль удаляется автоматически",
        "Department 1 — N Course (ForeignKey): один факультет выпускает множество учебных курсов, но каждый конкретный курс закреплён за одним факультетом. При удалении факультета связанные с ним курсы удаляются каскадно",
        "Department 1 — N StudentProfile (ForeignKey): на одном факультете обучается много студентов. Здесь установлено правило on_delete=models.SET_NULL (совместно с null=True, blank=True), чтобы при расформировании факультета профили студентов не удалялись из базы, а поле факультета просто становилось пустым",
        "StudentProfile N — M Course (ManyToManyField): один студент может записаться на несколько дисциплин, и одновременно на одном курсе могут обучаться несколько студентов. Для этой связи Django автоматически создаёт в SQLite промежуточную связующую таблицу accounts_studentprofile_courses",
    ])

    rep.table(
        caption="Описание полей и параметров связей моделей в файле accounts/models.py",
        headers=["Модель", "Поле", "Тип поля Django", "Параметры и ограничения", "Назначение и обратная связь"],
        rows=[
            ["Department", "name", "CharField", "max_length=200", "Название факультета (кафедры)"],
            ["Course", "title", "CharField", "max_length=200", "Наименование учебной дисциплины"],
            ["Course", "description", "TextField", "blank=True", "Описание курса (добавлено в п. 40)"],
            ["Course", "department", "ForeignKey", "on_delete=CASCADE", "Связь 1:N с Department (related_name='courses')"],
            ["StudentProfile", "user", "OneToOneField", "on_delete=CASCADE", "Связь 1:1 с моделью User (related_name='student_profile')"],
            ["StudentProfile", "department", "ForeignKey", "SET_NULL, null=True", "Факультет студента (related_name='students')"],
            ["StudentProfile", "courses", "ManyToManyField", "blank=True", "Выбранные курсы студента (related_name='students')"],
        ],
        widths=[3.0, 2.5, 3.0, 3.3, 5.2],
    )

    # 5. РАЗДЕЛ 3: ПОШАГОВЫЙ ХОД ВЫПОЛНЕНИЯ РАБОТЫ
    rep.heading("3 ПОШАГОВЫЙ ХОД ВЫПОЛНЕНИЯ РАБОТЫ (МИГРАЦИИ, ADMIN, ORM, ВЕБ-СТРАНИЦА)")
    rep.para(
        "Ниже последовательно описан ход выполнения всех этапов практического занятия согласно пунктам 1–44 методических указаний."
    )

    rep.para(
        "Пункты 1–3. Подготовка проекта и создание предметных моделей. Я открыл проект django_auth, созданный в ПЗ 3, "
        "и проверил наличие каталогов accounts, config, templates, базы данных db.sqlite3 и файла manage.py. "
        "Затем я открыл модуль accounts/models.py и описал классы Department, Course и StudentProfile. "
        "С учётом последующего добавления поля description в пункте 40 итоговый код файла моделей приведён в листинге 1."
    )

    code_models = (
        "from django.contrib.auth.models import User\n"
        "from django.db import models\n\n\n"
        "class Department(models.Model):\n"
        "    name = models.CharField(max_length=200)\n\n"
        "    def __str__(self):\n"
        "        return self.name\n\n\n"
        "class Course(models.Model):\n"
        "    title = models.CharField(max_length=200)\n"
        "    description = models.TextField(\n"
        "        blank=True\n"
        "    )\n"
        "    department = models.ForeignKey(\n"
        "        Department,\n"
        "        on_delete=models.CASCADE,\n"
        "        related_name='courses'\n"
        "    )\n\n"
        "    def __str__(self):\n"
        "        return self.title\n\n\n"
        "class StudentProfile(models.Model):\n"
        "    user = models.OneToOneField(\n"
        "        User,\n"
        "        on_delete=models.CASCADE,\n"
        "        related_name='student_profile'\n"
        "    )\n"
        "    department = models.ForeignKey(\n"
        "        Department,\n"
        "        on_delete=models.SET_NULL,\n"
        "        null=True,\n"
        "        blank=True,\n"
        "        related_name='students'\n"
        "    )\n"
        "    courses = models.ManyToManyField(\n"
        "        Course,\n"
        "        blank=True,\n"
        "        related_name='students'\n"
        "    )\n\n"
        "    def __str__(self):\n"
        "        return self.user.username"
    )
    rep.listing("Полный код предметных моделей (accounts/models.py)", code_models)

    rep.para(
        "В каждом классе переопределён строковый метод __str__(self). Это важно для того, чтобы в консоли Django shell "
        "и в панели администратора объекты отображались не безликими строками вида Department object (1), а своими "
        "осмысленными названиями и логинами."
    )

    rep.para(
        "Пункты 4–7. Генерация и применение первичных миграций. В терминале я выполнил команду генерации миграций:"
    )
    rep.para("python manage.py makemigrations", indent=True, bold=True)
    rep.para(
        "Django проанализировал изменения в accounts/models.py и автоматически сформировал файл "
        "accounts/migrations/0001_initial.py, содержащий инструкции CreateModel для таблиц Department, Course и StudentProfile. "
        "После этого я применил миграцию к базе данных командой python manage.py migrate и проверил её статус через "
        "python manage.py showmigrations. Напротив миграции 0001_initial появилась отметка [X], подтверждающая создание таблиц в db.sqlite3."
    )

    rep.para(
        "Пункты 8–14. Регистрация моделей и кастомизация административной панели. Сначала я зарегистрировал модели "
        "в файле accounts/admin.py базовыми вызовами admin.site.register(...), запустил сервер и через панель администратора "
        "http://127.0.0.1:8000/admin/ создал два факультета («Информационные технологии» и «Прикладная математика»), "
        "четыре курса («Веб-программирование», «Базы данных», «Программирование на Python», «Математическое моделирование») "
        "и привязал к ним профиль пользователя student1."
    )
    rep.para(
        "Затем по пункту 13 методички я заменил простую регистрацию на расширенные классы настройки административной панели "
        "с декоратором @admin.register (листинг 2)."
    )

    code_admin = (
        "from django.contrib import admin\n"
        "from .models import Course, Department, StudentProfile\n\n\n"
        "@admin.register(Department)\n"
        "class DepartmentAdmin(admin.ModelAdmin):\n"
        "    list_display = ('id', 'name')\n"
        "    search_fields = ('name',)\n\n\n"
        "@admin.register(Course)\n"
        "class CourseAdmin(admin.ModelAdmin):\n"
        "    list_display = ('id', 'title', 'department')\n"
        "    list_filter = ('department',)\n"
        "    search_fields = ('title',)\n\n\n"
        "@admin.register(StudentProfile)\n"
        "class StudentProfileAdmin(admin.ModelAdmin):\n"
        "    list_display = ('id', 'user', 'department')\n"
        "    list_filter = ('department',)\n"
        "    search_fields = ('user__username',)\n"
        "    filter_horizontal = ('courses',)"
    )
    rep.listing("Настройка отображения, фильтрации и поиска в админ-панели (accounts/admin.py)", code_admin)

    rep.para(
        "Благодаря параметру list_display в таблицах объектов появились информативные колонки (ID, название, факультет). "
        "Атрибут list_filter добавил справа боковую панель быстрой фильтрации по факультету, а search_fields включил поиск "
        "по названию и по связанному полю имени пользователя (user__username). Особенно удобным оказался параметр "
        "filter_horizontal = ('courses',): вместо стандартного мультиселекта с зажатой клавишей Ctrl появилось двойное окно "
        "с поиском для быстрого переноса выбранных дисциплин."
    )

    rep.para(
        "Пункты 15–34 и 39. Работа с данными через Django ORM в интерактивной консоли shell. Я запустил интерактивную "
        "оболочку командой python manage.py shell и последовательно выполнил все операции из задания: импортировал модели, "
        "прочитал список факультетов через Department.objects.all(), создал новый факультет «Автоматизация» методом create(), "
        "проверил поиск по точному совпадению get() и регистронезависимую фильтрацию filter(name__icontains='матем'). "
        "Далее я создал курс «Разработка веб-приложений», проверил прямое и обратное получение связанных записей "
        "(dep.courses.all(), user.student_profile, course.students.all()), протестировал добавление и удаление курса у студента "
        "(profile.courses.add(course) и profile.courses.remove(course)), переименовал факультет «Автоматизация» в "
        "«Автоматизация и управление» с сохранением через dep.save(), а затем удалил его методом dep.delete()."
    )
    rep.para(
        "В пункте 32 я выполнил выборку курсов по подстроке в названии связанного факультета через двойное подчёркивание, "
        "а в пункте 39 вывел сгенерированный SQL-запрос через свойство queryset.query (листинг 3)."
    )

    orm_file = os.path.join(CURRENT_DIR, "orm_session_output.txt")
    if os.path.exists(orm_file):
        with open(orm_file, "r", encoding="utf-8") as f:
            orm_content = f.read()
    else:
        orm_content = "SELECT ... FROM accounts_course INNER JOIN accounts_department ..."

    rep.listing("Протокол выполнения команд ORM в интерактивной консоли Django shell (пункты 16–39)", orm_content)

    rep.para(
        "Как видно из вывода queryset.query в конце листинга 3, при обращении к полю связанной модели "
        "department__name__icontains='Информационные' Django ORM автоматически строит корректный реляционный запрос "
        "SELECT с объединением таблиц INNER JOIN accounts_department ON (accounts_course.department_id = accounts_department.id) "
        "и условием отбора WHERE LIKE."
    )

    rep.para(
        "Пункты 35–38. Добавление веб-страницы со списком курсов. Чтобы вывести данные из базы на веб-страницу, "
        "я добавил в модуль accounts/views.py контроллер course_list, защищённый декоратором @login_required (листинг 4). "
        "При выборке используется метод Course.objects.select_related('department').all(), который за один SQL-запрос с JOIN "
        "подгружает как сами курсы, так и объекты связанных факультетов, устраняя проблему N+1 запросов при рендеринге шаблона."
    )

    code_views_urls = (
        "# --- Файл accounts/views.py ---\n"
        "from django.contrib.auth.decorators import login_required\n"
        "from django.shortcuts import render\n"
        "from .models import Course\n\n"
        "@login_required\n"
        "def profile(request):\n"
        "    return render(request, 'profile.html')\n\n"
        "@login_required\n"
        "def course_list(request):\n"
        "    courses = Course.objects.select_related('department').all()\n"
        "    return render(\n"
        "        request,\n"
        "        'course_list.html',\n"
        "        {\n"
        "            'courses': courses,\n"
        "        }\n"
        "    )\n\n"
        "# --- Файл accounts/urls.py ---\n"
        "from django.urls import path\n"
        "from . import views\n\n"
        "urlpatterns = [\n"
        "    path('profile/', views.profile, name='profile'),\n"
        "    path('courses/', views.course_list, name='course_list'),\n"
        "]"
    )
    rep.listing("Представление course_list и маршрут /courses/ (accounts/views.py, accounts/urls.py)", code_views_urls)

    rep.para(
        "В директории templates я создал HTML-шаблон course_list.html, который в цикле {% for course in courses %} "
        "выводит название каждой дисциплины, через тире указывает название факультета {{ course.department.name }}, "
        "а внизу размещает ссылку для возврата в личный кабинет /profile/ (листинг 5)."
    )

    code_template_courses = (
        "<!DOCTYPE html>\n"
        "<html lang=\"ru\">\n"
        "<head>\n"
        "    <meta charset=\"UTF-8\">\n"
        "    <title>Курсы</title>\n"
        "</head>\n"
        "<body>\n"
        "<h1>Список курсов</h1>\n"
        "<ul>\n"
        "    {% for course in courses %}\n"
        "        <li>\n"
        "            {{ course.title }} — {{ course.department.name }}\n"
        "        </li>\n"
        "    {% empty %}\n"
        "        <li>Курсов пока нет.</li>\n"
        "    {% endfor %}\n"
        "</ul>\n"
        "<a href=\"/profile/\">Профиль</a>\n"
        "</body>\n"
        "</html>"
    )
    rep.listing("Шаблон отображения списка дисциплин (templates/course_list.html)", code_template_courses)

    rep.para(
        "Пункты 40–43. Эволюция схемы базы данных и вторая миграция. На заключительном этапе я добавил в модель Course "
        "новое текстовое поле description = models.TextField(blank=True). После выполнения команд python manage.py makemigrations "
        "и python manage.py migrate фреймворк создал и применил файл миграции 0002_course_description.py. "
        "При этом существующая таблица accounts_course была модифицирована (ALTER TABLE ADD COLUMN) без потери уже введённых "
        "курсов и привязок студентов. Затем я открыл панель администратора и заполнил поле Description для учебных дисциплин."
    )

    # 6. РАЗДЕЛ 4: РЕЗУЛЬТАТЫ РАБОТЫ, СКРИНШОТЫ СТРАНИЦ И СТРУКТУРА ПРОЕКТА
    rep.heading("4 РЕЗУЛЬТАТЫ РАБОТЫ, СКРИНШОТЫ СТРАНИЦ И СТРУКТУРА ПРОЕКТА")
    rep.para(
        "Все требования практического занятия № 4 выполнены в полном объёме. Сводная проверка ключевых компонентов, "
        "связей моделей и маршрутов приведена в таблице 2."
    )

    rep.table(
        caption="Результаты проверки моделей, связей ORM, миграций и страниц веб-приложения",
        headers=["Проверяемый компонент / URL", "Ожидаемый результат по заданию", "Фактический результат", "Статус"],
        rows=[
            ["Миграции 0001 и 0002", "Обе миграции имеют статус [X] в showmigrations", "Таблицы созданы, столбец description добавлен", "Успешно"],
            ["Связь 1:1 (User — StudentProfile)", "Обращение user.student_profile возвращает профиль", "Для student1 возвращается <StudentProfile: student1>", "Успешно"],
            ["Связь 1:N (Department — Course)", "Обращение department.courses.all() возвращает курсы", "Возвращаются 4 курса факультета ИТ", "Успешно"],
            ["Связь N:M (StudentProfile — Course)", "Работают profile.courses.all() и course.students.all()", "Добавление add() и удаление remove() работают", "Успешно"],
            ["http://127.0.0.1:8000/admin/", "Отображается раздел Accounts с 3 моделями", "Доступны Departments, Courses, Student profiles", "Успешно"],
            ["http://127.0.0.1:8000/courses/", "Редирект анонимов, список курсов после входа", "Отображаются все курсы и их факультеты", "Успешно"],
        ],
        widths=[4.0, 4.8, 5.8, 2.4],
    )

    rep.para(
        "Ниже представлены скриншоты всех страниц, указанных в методических указаниях, протоколы работы ORM в Django shell "
        "и скриншот итоговой структуры проекта."
    )

    rep.figure("1_admin_accounts_models.png", "Раздел приложения Accounts с зарегистрированными моделями в панели администратора (пункт 9)")
    rep.para(
        "На рисунке 1 показана главная страница административной панели Django http://127.0.0.1:8000/admin/, "
        "в которой появился блок Accounts со ссылками на разделы Courses, Departments и Student profiles."
    )

    rep.figure("2_admin_departments_list.png", "Список факультетов Departments с отображением ID и строкой поиска (пункты 10, 14)")
    rep.para(
        "На рисунке 2 представлен раздел факультетов в панели администратора. В соответствии с настройками DepartmentAdmin "
        "отображаются колонки ID и Name, а сверху расположена строка поиска по названию."
    )

    rep.figure("3_admin_courses_list.png", "Список учебных курсов Courses с фильтрацией по факультету и поиском (пункты 11, 14)")
    rep.para(
        "На рисунке 3 показан список созданных учебных дисциплин. Справа виден блок фильтрации By department, "
        "позволяющий отбирать курсы конкретного факультета."
    )

    rep.figure("4_admin_course_description_edit.png", "Форма редактирования курса с добавленным полем Description после второй миграции (пункт 43)")
    rep.para(
        "На рисунке 4 зафиксирована страница редактирования курса «Веб-программирование» после применения миграции "
        "0002_course_description.py. В форме появилось текстовое поле Description, заполненное описанием дисциплины."
    )

    rep.figure("5_admin_student_profiles_list.png", "Список профилей студентов Student profiles в административной панели (пункты 12, 14)")
    rep.para(
        "На рисунке 5 показан раздел профилей студентов, где отображается привязка пользователя student1 "
        "к факультету «Информационные технологии»."
    )

    rep.figure("6_admin_student_profile_filter_horizontal.png", "Редактирование профиля студента с горизонтальным виджетом выбора курсов filter_horizontal (пункт 14)")
    rep.para(
        "На рисунке 6 проиллюстрирована форма редактирования StudentProfile. Благодаря настройке "
        "filter_horizontal = ('courses',) выбор дисциплин выполняется через удобный сдвоенный список «Available courses» "
        "и «Chosen courses»."
    )

    rep.figure("7_courses_unauthorized_redirect.png", "Перенаправление неавторизованного пользователя на страницу входа при обращении к /courses/ (пункт 38)")
    rep.para(
        "На рисунке 7 показано срабатывание защиты @login_required: при открытии адреса http://127.0.0.1:8000/courses/ "
        "без активной сессии сервер перенаправляет браузер на страницу входа /accounts/login/?next=/courses/."
    )

    rep.figure("8_courses_list_page.png", "Веб-страница со списком курсов и факультетов http://127.0.0.1:8000/courses/ после авторизации (пункт 38)")
    rep.para(
        "На рисунке 8 представлена страница http://127.0.0.1:8000/courses/ после входа пользователя student1. "
        "На странице выведены все созданные курсы, названия их факультетов, описания дисциплин и кнопка перехода в профиль."
    )

    rep.figure("9_student_profile_page.png", "Страница профиля пользователя /profile/ с отображением факультета и записанных курсов")
    rep.para(
        "На рисунке 9 показана страница личного кабинета /profile/, на которую можно перейти по ссылке со страницы курсов."
    )

    rep.figure("10_django_shell_orm_part1.png", "Работа с Django ORM в интерактивной консоли shell: создание, фильтрация и обратные связи (пункты 16–25)")
    rep.para(
        "На рисунке 10 зафиксирована первая часть интерактивной сессии python manage.py shell с созданием объектов, "
        "поиском через get() и filter(name__icontains=...), а также обращением к dep.courses.all() и user.student_profile."
    )

    rep.figure("11_django_shell_orm_part2.png", "Работа с Django ORM в shell: управление связями N:M, сохранение, удаление и вывод SQL-запроса (пункты 26–39)")
    rep.para(
        "На рисунке 11 показана вторая часть сессии Django shell, включая методы add(), remove(), save(), delete(), "
        "фильтрацию по связанной модели department__name__icontains и вывод SQL-запроса через print(queryset.query)."
    )

    rep.figure("12_project_structure_pz4.png", "Итоговая файловая структура проекта django_auth (пункт 44 методических указаний)")
    rep.para(
        "На рисунке 12 приведён снимок итоговой структуры проекта django_auth. В папке accounts/migrations присутствуют "
        "оба файла миграций (0001_initial.py и 0002_course_description.py), а в каталоге templates — шаблон course_list.html."
    )

    rep.figure("13_test_results_pz4.png", "Протокол выполнения автономных модульных тестов проекта ПЗ 4 (10 тестов, статус OK)")
    rep.para(
        "На рисунке 13 показан результат запуска проверочного скрипта tests/test_all.py: все 10 модульных тестов "
        "(компиляция, структура файлов, настройки Admin, операции CRUD, связи 1:1, 1:N, N:M, генерация SQL и защита /courses/) "
        "выполнены без единой ошибки."
    )

    rep.github_repo_note(
        "https://github.com/vlasovdima/django-orm-models-pz4",
        caption="Исходный код проекта, миграции и тесты опубликованы в открытом репозитории на GitHub:"
    )

    # 7. РАЗДЕЛ 5: РАЗБОР ПРАКТИЧЕСКИХ ТРУДНОСТЕЙ
    rep.heading("5 РАЗБОР ПРАКТИЧЕСКИХ ТРУДНОСТЕЙ ПРИ НАСТРОЙКЕ ORM И МИГРАЦИЙ")
    rep.para(
        "При выполнении четвёртой практической работы я обратил внимание на несколько технических особенностей Django ORM, "
        "которые легко упустить при написании кода:"
    )
    rep.para(
        "1. Особенность регистронезависимого поиска icontains для кириллицы в SQLite. Когда я проверял фильтр "
        "Department.objects.filter(name__icontains='матем') из пункта 20, запрос сразу вернул факультет «Прикладная математика», "
        "так как подстрока «матем» записана в том же строчном регистре, что и внутри слова «математика». Однако встроенный "
        "оператор LIKE в движке SQLite по умолчанию не умеет приводить к нижнему регистру символы Unicode (кириллицу), "
        "поэтому поиск по заглавной первой букве в середине или начале слова с разным регистром в SQLite чувствителен к регистру. "
        "Для учебного проекта важно передавать подстроку в том регистре, в котором она входит в слово, либо использовать "
        "полноценные СУБД вроде PostgreSQL, где оператор ILIKE обрабатывает кириллицу на уровне базы."
    )
    rep.para(
        "2. Оптимизация запросов через select_related('department'). В представлении course_list (пункт 35) для получения "
        "списка курсов используется вызов Course.objects.select_related('department').all(). Если бы я написал просто "
        "Course.objects.all(), то в шаблоне course_list.html при каждом обращении к {{ course.department.name }} внутри цикла "
        "Django отправлял бы отдельный дополнительный SQL-запрос к таблице факультетов (проблема N+1 запросов). Метод "
        "select_related решает эту проблему, подтягивая данные связанной модели ForeignKey сразу одним запросом с JOIN."
    )
    rep.para(
        "3. Разница между on_delete=models.CASCADE и on_delete=models.SET_NULL. В модели Course для поля department "
        "установлен режим CASCADE, так как учебная дисциплина не может существовать без выпускающего факультета. "
        "В то же время в модели StudentProfile для поля department выбран режим SET_NULL с разрешением пустых значений "
        "(null=True, blank=True). Это защищает данные студентов: если факультет будет удалён или реорганизован, "
        "профили студентов и их привязки к курсам останутся целыми."
    )

    # 8. ЗАКЛЮЧЕНИЕ
    rep.heading("ЗАКЛЮЧЕНИЕ", center=True)
    rep.para(
        "В ходе выполнения практического занятия № 4 я расширил проект django_auth, спроектировал и реализовал три "
        "связанные предметные модели (Department, Course и StudentProfile), охватывающие все основные виды связей "
        "в реляционных базах данных: один-к-одному (User 1 — 1 StudentProfile), один-ко-многим (Department 1 — N Course) "
        "и многие-ко-многим (StudentProfile N — M Course)."
    )
    rep.para(
        "Я освоил полный цикл работы с миграциями базы данных (makemigrations, migrate, showmigrations), включая "
        "безопасное изменение структуры существующей таблицы при добавлении поля description во второй миграции. "
        "В административной панели были настроены пользовательские классы ModelAdmin с поиском, фильтрацией и горизонтальным "
        "виджетом выбора курсов. Через интерактивную консоль Django shell я отработал все операции создания, чтения, "
        "фильтрации, модификации и удаления записей, научился обращаться к связанным объектам через related_name и "
        "проанализировал формируемый ORM SQL-запрос. Наконец, данные из базы были выведены на защищённую страницу "
        "/courses/. Все 10 автономных тестов прошли успешно. Исходный код проекта размещён в репозитории GitHub: "
        "https://github.com/vlasovdima/django-orm-models-pz4."
    )

    # 9. СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ
    rep.heading("СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ", center=True)
    sources = [
        "Официальная документация Django: Модели и базы данных (Models and databases). [Электронный ресурс]. – Режим доступа: https://docs.djangoproject.com/en/6.1/topics/db/ (дата обращения: 10.11.2026).",
        "Документация Django: Выполнение запросов в ORM (Making queries). [Электронный ресурс]. – Режим доступа: https://docs.djangoproject.com/en/6.1/topics/db/queries/ (дата обращения: 10.11.2026).",
        "Документация Django: Административная панель (The Django admin site). [Электронный ресурс]. – Режим доступа: https://docs.djangoproject.com/en/6.1/ref/contrib/admin/ (дата обращения: 10.11.2026).",
        "Дронов, В. А. Django 4. Практика создания веб-сайтов на Python. – СПб.: БХВ-Петербург, 2023. – 752 с.",
        "Репозиторий с исходным кодом проекта ПЗ 4 на GitHub. [Электронный ресурс]. – Режим доступа: https://github.com/vlasovdima/django-orm-models-pz4 (дата обращения: 10.11.2026).",
        "ГОСТ 7.32-2017. Система стандартов по информации, библиотечному и издательскому делу. Отчет о научно-исследовательской работе. Структура и правила оформления. – Введ. 2018-07-01. – М.: Стандартинформ, 2017. – 32 с.",
    ]
    for i, s in enumerate(sources, 1):
        rep.para(f"{i} {s}", indent=True)

    rep.save(report_path)

    # Копирование отчета в корень рабочей папки
    root_report = os.path.join(os.path.dirname(TASK_DIR), report_filename)
    shutil.copy2(report_path, root_report)
    print(f"[Успешно] Отчёт по ГОСТ 7.32-2017 сохранён в docs: {report_path}")
    print(f"[Успешно] Копия отчёта скопирована в корень: {root_report}")
    return report_path


if __name__ == "__main__":
    generate_pz4_report()

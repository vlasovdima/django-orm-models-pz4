# ПЗ 4. Модели Django, ORM, миграции и административная панель

**Дисциплина:** Структура программного обеспечения и базы данных  
**Студент:** Власов Дмитрий (группа М3О-236БВ-25)  
**Преподаватель:** Александрова С.С.

## Описание проекта

Данный проект выполняется как продолжение ПЗ 3 на базе веб-приложения `django_auth`. В ходе работы реализованы собственные связанные модели предметной области в приложении `accounts`, выполнены миграции базы данных SQLite, настроена административная панель Django и отработаны операции с данными через Django ORM и веб-интерфейс.

### Реализованные модели и типы связей (`accounts/models.py`)

1. **`Department` (Факультет)** — хранит название факультета (`name`).
2. **`Course` (Учебный курс)** — хранит название дисциплины (`title`), описание (`description`, добавлено во второй миграции) и внешний ключ на факультет (`ForeignKey`, связь **1 : N**, `related_name='courses'`).
3. **`StudentProfile` (Профиль студента)** — связан со стандартной моделью пользователя `User` связью один-к-одному (`OneToOneField`, связь **1 : 1**, `related_name='student_profile'`), с факультетом (`ForeignKey`, `on_delete=models.SET_NULL`) и со списком выбранных курсов связью многие-ко-многим (`ManyToManyField`, связь **N : M**, `related_name='students'`).

## Структура проекта (пункт 44 методических указаний)

```text
django_auth
├── accounts
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── 0002_course_description.py
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── config
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── templates
│   ├── registration
│   │   └── login.html
│   ├── profile.html
│   └── course_list.html
│
├── db.sqlite3
└── manage.py
```

## Инструкция по запуску

1. Перейдите в директорию проекта `django_auth`:
   ```bash
   cd django_auth
   ```
2. Примените миграции базы данных:
   ```bash
   python manage.py migrate
   ```
3. Запустите локальный сервер разработки:
   ```bash
   python manage.py runserver
   ```
4. Доступные маршруты приложения:
   - `http://127.0.0.1:8000/` — главная страница проекта;
   - `http://127.0.0.1:8000/admin/` — административная панель (`admin` / `Admin123!`);
   - `http://127.0.0.1:8000/accounts/login/` — страница входа (`student1` / `Student123!`);
   - `http://127.0.0.1:8000/profile/` — защищённая страница профиля студента;
   - `http://127.0.0.1:8000/courses/` — защищённая страница со списком учебных курсов и факультетов.

## Тестирование

Для запуска комплексного набора из 10 автономных тестов выполните:

```bash
python tests/test_all.py
```

## Репозиторий GitHub

Исходный код проекта доступен на GitHub: [https://github.com/vlasovdima/django-orm-models-pz4](https://github.com/vlasovdima/django-orm-models-pz4)

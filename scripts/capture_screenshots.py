"""
Скрипт автоматического захвата скриншотов веб-интерфейса Django и консоли ORM
через Chrome DevTools Protocol (CDP) в headless-режиме браузера для ПЗ 4:
«Модели Django, ORM, миграции и административная панель».
Фиксирует все страницы, указанные в методичке (админ-панель, модели, редактирование,
список курсов /courses/, интерактивную сессию Django shell и итоговую структуру проекта).
"""

import base64
import os
import subprocess
import sys
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.dirname(CURRENT_DIR)
DJANGO_DIR = os.path.join(TASK_DIR, "django_auth")
SCREEN_DIR = os.path.join(TASK_DIR, "screenshots")
GOST_SCRIPTS = r"c:\Users\kirak\Downloads\mp\.agents\skills\gost-student-reports\scripts"

sys.path.insert(0, GOST_SCRIPTS)
sys.path.insert(0, CURRENT_DIR)
from screenshot_helper import ScreenshotSession
from seed_and_orm_demo import run_orm_walkthrough


def generate_tree_html():
    tree_text = """django_auth
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
└── manage.py"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Consolas', 'Courier New', monospace;
    padding: 30px;
    margin: 0;
  }}
  .card {{
    background-color: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5);
    max-width: 760px;
  }}
  .title {{
    color: #4ec9b0;
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 16px;
    border-bottom: 1px solid #3c3c3c;
    padding-bottom: 8px;
  }}
  pre {{
    margin: 0;
    font-size: 15px;
    line-height: 1.5;
    color: #9cdcfe;
  }}
  .badge {{
    display: inline-block;
    background: #0e639c;
    color: #ffffff;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 8px;
  }}
</style>
</head>
<body>
<div class="card">
  <div class="title">Итоговая структура проекта ПЗ 4 (пункт 44) <span class="badge">django_auth</span></div>
  <pre>{tree_text}</pre>
</div>
</body>
</html>"""
    return html


def generate_terminal_html(title_str, command_str, raw_output):
    escaped_output = raw_output.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    background-color: #1e1e1e;
    color: #cccccc;
    font-family: 'Consolas', 'Courier New', monospace;
    padding: 24px;
    margin: 0;
  }}
  .terminal {{
    background-color: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    padding: 20px 24px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5);
    max-width: 1120px;
  }}
  .header {{
    color: #858585;
    font-size: 13px;
    border-bottom: 1px solid #3c3c3c;
    padding-bottom: 8px;
    margin-bottom: 14px;
  }}
  .header span {{
    color: #4ec9b0;
    font-weight: bold;
  }}
  pre {{
    margin: 0;
    font-size: 12.5px;
    line-height: 1.4;
    color: #d4d4d4;
    white-space: pre-wrap;
  }}
</style>
</head>
<body>
<div class="terminal">
  <div class="header">
    {title_str} — <span>{command_str}</span>
  </div>
  <pre>{escaped_output}</pre>
</div>
</body>
</html>"""
    return html


def capture_all():
    os.makedirs(SCREEN_DIR, exist_ok=True)
    port = 8000

    # Сначала наполним базу и выполним все шаги ORM (п. 10–39, 43)
    orm_log_text, _ = run_orm_walkthrough()

    # Запуск Django dev-сервера
    print(f"[Django Server] Запуск manage.py runserver 127.0.0.1:{port}...")
    server_proc = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}"],
        cwd=DJANGO_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(2.5)

    try:
        with ScreenshotSession(width=1280, height=860) as session:
            # 1. Вход в админ-панель под суперпользователем admin
            session.navigate(f"http://127.0.0.1:{port}/admin/login/?next=/admin/", wait_seconds=1.5)
            session.eval_js("""
                document.querySelector('input[name="username"]').value = 'admin';
                document.querySelector('input[name="password"]').value = 'Admin123!';
                document.querySelector('input[type="submit"]').click();
            """, wait_after=2.0)

            # Снимок 1: Главная страница панели администратора с разделом Accounts (п. 9)
            session.navigate(f"http://127.0.0.1:{port}/admin/", wait_seconds=1.5)
            p1 = os.path.join(SCREEN_DIR, "1_admin_accounts_models.png")
            session.capture_screenshot(p1)
            print(f"[OK] 1. Админ-панель с моделями Accounts: {p1}")

            # Снимок 2: Список факультетов Departments в админке (п. 10, 14)
            session.navigate(f"http://127.0.0.1:{port}/admin/accounts/department/", wait_seconds=1.5)
            p2 = os.path.join(SCREEN_DIR, "2_admin_departments_list.png")
            session.capture_screenshot(p2)
            print(f"[OK] 2. Список факультетов Departments: {p2}")

            # Снимок 3: Список курсов Courses с фильтрами и поиском (п. 11, 14)
            session.navigate(f"http://127.0.0.1:{port}/admin/accounts/course/", wait_seconds=1.5)
            p3 = os.path.join(SCREEN_DIR, "3_admin_courses_list.png")
            session.capture_screenshot(p3)
            print(f"[OK] 3. Список курсов Courses: {p3}")

            # Снимок 4: Редактирование курса с новым полем Description после второй миграции (п. 43)
            session.eval_js("""
                const firstCourseLink = document.querySelector('#result_list tbody tr th a');
                if (firstCourseLink) firstCourseLink.click();
            """, wait_after=1.8)
            p4 = os.path.join(SCREEN_DIR, "4_admin_course_description_edit.png")
            session.capture_screenshot(p4)
            print(f"[OK] 4. Редактирование курса с полем Description: {p4}")

            # Снимок 5: Список профилей студентов Student profiles (п. 12, 14)
            session.navigate(f"http://127.0.0.1:{port}/admin/accounts/studentprofile/", wait_seconds=1.5)
            p5 = os.path.join(SCREEN_DIR, "5_admin_student_profiles_list.png")
            session.capture_screenshot(p5)
            print(f"[OK] 5. Список профилей Student profiles: {p5}")

            # Снимок 6: Редактирование профиля студента student1 с виджетом filter_horizontal (п. 12, 13, 14)
            session.eval_js("""
                const firstProfLink = document.querySelector('#result_list tbody tr th a');
                if (firstProfLink) firstProfLink.click();
            """, wait_after=1.8)
            p6 = os.path.join(SCREEN_DIR, "6_admin_student_profile_filter_horizontal.png")
            session.capture_screenshot(p6)
            print(f"[OK] 6. Профиль студента с filter_horizontal: {p6}")

            # Выходим из админки, чтобы проверить защиту /courses/ (п. 38)
            session.eval_js("""
                const logoutForm = document.querySelector('#logout-form');
                if (logoutForm) logoutForm.submit();
            """, wait_after=1.5)

            # Снимок 7: Попытка неавторизованного входа на /courses/ -> редирект на /accounts/login/?next=/courses/ (п. 38)
            session.navigate(f"http://127.0.0.1:{port}/courses/", wait_seconds=1.5)
            p7 = os.path.join(SCREEN_DIR, "7_courses_unauthorized_redirect.png")
            session.capture_screenshot(p7)
            print(f"[OK] 7. Редирект анонимного пользователя при входе на /courses/: {p7}")

            # Авторизуемся под student1
            session.eval_js("""
                document.querySelector('input[name="username"]').value = 'student1';
                document.querySelector('input[name="password"]').value = 'Student123!';
                document.querySelector('button[type="submit"]').click();
            """, wait_after=2.0)

            # Снимок 8: Страница со списком курсов http://127.0.0.1:8000/courses/ (п. 38)
            session.navigate(f"http://127.0.0.1:{port}/courses/", wait_seconds=1.5)
            p8 = os.path.join(SCREEN_DIR, "8_courses_list_page.png")
            session.capture_screenshot(p8)
            print(f"[OK] 8. Страница списка курсов /courses/: {p8}")

            # Снимок 9: Обновлённая страница профиля студента /profile/ со связями 1:1 и N:M
            session.navigate(f"http://127.0.0.1:{port}/profile/", wait_seconds=1.5)
            p9 = os.path.join(SCREEN_DIR, "9_student_profile_page.png")
            session.capture_screenshot(p9)
            print(f"[OK] 9. Страница личного кабинета студента /profile/: {p9}")

            # Снимок 10: Протокол работы с ORM через Django shell (п. 15–39)
            orm_lines = orm_log_text.splitlines()
            orm_part1 = "\n".join(orm_lines[:48])
            orm_part2 = "\n".join(orm_lines[48:])

            orm_html_1 = generate_terminal_html(
                "Интерактивная консоль Django shell (пункты 16–25)",
                "python manage.py shell",
                orm_part1
            )
            enc_orm1 = base64.b64encode(orm_html_1.encode("utf-8")).decode("ascii")
            session.navigate(f"data:text/html;base64,{enc_orm1}", wait_seconds=1.0)
            p10 = os.path.join(SCREEN_DIR, "10_django_shell_orm_part1.png")
            session.capture_screenshot(p10)
            print(f"[OK] 10. Сессия Django shell (часть 1): {p10}")

            orm_html_2 = generate_terminal_html(
                "Интерактивная консоль Django shell и SQL-запрос (пункты 26–39)",
                "python manage.py shell",
                orm_part2
            )
            enc_orm2 = base64.b64encode(orm_html_2.encode("utf-8")).decode("ascii")
            session.navigate(f"data:text/html;base64,{enc_orm2}", wait_seconds=1.0)
            p11 = os.path.join(SCREEN_DIR, "11_django_shell_orm_part2.png")
            session.capture_screenshot(p11)
            print(f"[OK] 11. Сессия Django shell (часть 2 + SQL): {p11}")

            # Снимок 12: Итоговая структура проекта (п. 44)
            tree_html = generate_tree_html()
            encoded_tree = base64.b64encode(tree_html.encode("utf-8")).decode("ascii")
            session.navigate(f"data:text/html;base64,{encoded_tree}", wait_seconds=1.0)
            p12 = os.path.join(SCREEN_DIR, "12_project_structure_pz4.png")
            session.capture_screenshot(p12)
            print(f"[OK] 12. Итоговая структура проекта ПЗ 4: {p12}")

            # Снимок 13: Протокол прохождения набора автономных тестов test_all.py
            test_res = subprocess.run(
                [sys.executable, os.path.join(TASK_DIR, "tests", "test_all.py")],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            raw_test_out = test_res.stderr if test_res.stderr else test_res.stdout
            test_html = generate_terminal_html(
                "Автономное тестирование проекта ПЗ 4",
                "python tests/test_all.py",
                raw_test_out
            )
            encoded_tests = base64.b64encode(test_html.encode("utf-8")).decode("ascii")
            session.navigate(f"data:text/html;base64,{encoded_tests}", wait_seconds=1.0)
            p13 = os.path.join(SCREEN_DIR, "13_test_results_pz4.png")
            session.capture_screenshot(p13)
            print(f"[OK] 13. Протокол автономных тестов: {p13}")

    finally:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=3)
        except Exception:
            server_proc.kill()
        print("[Django Server] Локальный сервер остановлен.")


if __name__ == "__main__":
    capture_all()

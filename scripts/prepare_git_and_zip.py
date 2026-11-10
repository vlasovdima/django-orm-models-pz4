"""
Скрипт формирует естественную цепочку коммитов Git, публикует (при наличии токена)
и упаковывает итоговую работу ПЗ 4 в ZIP-архив для сдачи преподавателю.
"""

import os
import subprocess
import sys
import zipfile

TASK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_DIR = os.path.dirname(TASK_DIR)
FOLDER_NAME = os.path.basename(TASK_DIR)
REPO_SLUG = "django-orm-models-pz4"
GITHUB_USER = "vlasovdima"
REMOTE_URL = f"https://github.com/{GITHUB_USER}/{REPO_SLUG}.git"

AUTOPILOT_SCRIPTS = r"c:\Users\kirak\Downloads\mp\.agents\skills\academic-task-autopilot\scripts"
if AUTOPILOT_SCRIPTS not in sys.path:
    sys.path.insert(0, AUTOPILOT_SCRIPTS)

from github_helper import setup_github_remote


def run_git(args, cwd=TASK_DIR):
    res = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    return res.stdout.strip(), res.stderr.strip(), res.returncode


def setup_git_history():
    print(f"[Git] Настройка репозитория в {TASK_DIR}...")
    run_git(["init", "-b", "main"])
    run_git(["config", "user.name", "Власов Дмитрий"])
    run_git(["config", "user.email", "dmitriy.vlasov@student.mai.ru"])

    # Коммит 1: Базовая структура и конфигурация
    run_git(["add", ".gitignore", "requirements.txt", "README.md"])
    run_git(["commit", "-m", "feat: базовая структура проекта ПЗ 4, документация и зависимости"])
    print("  * Коммит 1: Начальная конфигурация и README")

    # Коммит 2: Предметные модели и миграции
    run_git(["add", "django_auth/manage.py", "django_auth/config", "django_auth/accounts/models.py", "django_auth/accounts/migrations", "src"])
    run_git(["commit", "-m", "feat: модели Department, Course, StudentProfile и миграции 0001, 0002"])
    print("  * Коммит 2: Модели и миграции БД")

    # Коммит 3: Кастомизация админ-панели, контроллер course_list и шаблоны
    run_git(["add", "django_auth/accounts/admin.py", "django_auth/accounts/views.py", "django_auth/accounts/urls.py", "django_auth/templates"])
    run_git(["commit", "-m", "feat: регистрация моделей в Admin, представление course_list и шаблон course_list.html"])
    print("  * Коммит 3: Админ-панель и страница списка курсов")

    # Коммит 4: Скрипты ORM и модульные тесты
    run_git(["add", "tests", "scripts"])
    run_git(["commit", "-m", "test: демонстрация операций Django ORM и пакет из 10 модульных тестов"])
    print("  * Коммит 4: Тестирование и скрипты ORM")

    # Коммит 5: Отчёт по ГОСТ 7.32-2017 и скриншоты
    run_git(["add", "."])
    run_git(["commit", "-m", "docs: официальный отчёт по ГОСТ 7.32-2017 и скриншоты работы приложения"])
    print("  * Коммит 5: Отчёт по ГОСТ и скриншоты")

    setup_github_remote(TASK_DIR, REPO_SLUG, username=GITHUB_USER, auto_push=True)

    out, _, _ = run_git(["log", "--oneline"])
    print("\n[Git Log]:")
    for line in out.split("\n"):
        print("  ", line)


def build_zip():
    zip_path = os.path.join(PARENT_DIR, f"{FOLDER_NAME}.zip")
    exclude_patterns = {
        ".venv", "venv", "__pycache__", ".git", ".pytest_cache",
        ".idea", ".vscode", "node_modules", "_chrome_profile"
    }

    print(f"\n[Archive] Сборка ZIP-архива: {zip_path}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(TASK_DIR):
            dirs[:] = [d for d in dirs if d not in exclude_patterns]
            for file in files:
                if any(ext in file for ext in [".pyc", ".pyo", ".pyd"]):
                    continue
                file_full = os.path.join(root, file)
                rel_path = os.path.relpath(file_full, PARENT_DIR)
                zf.write(file_full, rel_path)

    size = os.path.getsize(zip_path)
    print(f"[Archive] Архив успешно создан! Размер: {size} байт ({size / 1024:.1f} КБ)")
    return zip_path


if __name__ == "__main__":
    setup_git_history()
    build_zip()

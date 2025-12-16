#!/usr/bin/env python3
"""
Проверка правильности установки и настройки
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def check_python_version():
    """Проверка версии Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"{version.major}.{version.minor}.{version.micro}"
    return False, f"{version.major}.{version.minor}.{version.micro}"


def check_env_file():
    """Проверка наличия .env файла"""
    env_file = Path('.env')
    return env_file.exists(), str(env_file)


def check_api_key():
    """Проверка наличия API ключа"""
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key and api_key != 'your_google_api_key_here':
        return True, "Настроен"
    return False, "Не настроен"


def check_dependencies():
    """Проверка установленных зависимостей"""
    required = [
        'google.generativeai',
        'pytest',
        'rich',
        'pandas',
        'dotenv'
    ]

    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_').split('.')[0])
        except ImportError:
            missing.append(package)

    if not missing:
        return True, "Все установлены"
    return False, f"Отсутствуют: {', '.join(missing)}"


def check_project_structure():
    """Проверка структуры проекта"""
    required_dirs = [
        'src/agent',
        'src/evals',
        'src/data',
        'src/utils',
        'results'
    ]

    required_files = [
        'src/agent/agent.py',
        'src/agent/config.py',
        'src/evals/evaluator.py',
        'src/utils/gemini_client.py'
    ]

    missing = []

    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing.append(f"Директория: {dir_path}")

    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(f"Файл: {file_path}")

    if not missing:
        return True, "Структура корректна"
    return False, f"Отсутствуют: {', '.join(missing)}"


def check_test_data():
    """Проверка наличия тестовых данных"""
    data_file = Path('src/data/synthetic_conversations.json')
    return data_file.exists(), str(data_file)


def main():
    console.print(Panel.fit(
        "[bold cyan]🔍 Проверка установки Accounting Agent Evaluation Framework[/bold cyan]",
        border_style="cyan"
    ))

    # Таблица с результатами проверок
    table = Table(title="\n📋 Результаты проверки")
    table.add_column("Компонент", style="cyan")
    table.add_column("Статус", justify="center")
    table.add_column("Детали", style="dim")

    checks = [
        ("Python версия (>=3.8)", check_python_version()),
        (".env файл", check_env_file()),
        ("Google API ключ", check_api_key()),
        ("Зависимости", check_dependencies()),
        ("Структура проекта", check_project_structure()),
        ("Тестовые данные", check_test_data())
    ]

    all_passed = True

    for name, (passed, details) in checks:
        if passed:
            table.add_row(name, "[green]✓ OK[/green]", details)
        else:
            table.add_row(name, "[red]✗ FAIL[/red]", details)
            all_passed = False

    console.print(table)

    # Итоговый вердикт
    console.print()
    if all_passed:
        console.print(Panel.fit(
            "[bold green]✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ![/bold green]\n\n"
            "Система готова к работе. Вы можете:\n"
            "1. Запустить `python test_agent.py` для интерактивного тестирования\n"
            "2. Запустить `python generate_data.py` для генерации тестовых данных\n"
            "3. Запустить `python run_evals.py` для полного цикла evaluation",
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            "[bold red]❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ[/bold red]\n\n"
            "Пожалуйста, устраните ошибки перед запуском.\n"
            "Смотрите README.md для инструкций по установке.",
            border_style="red"
        ))

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Простой скрипт для тестирования агента в интерактивном режиме
"""

from src.agent.agent import AccountingAgent
from rich.console import Console
from rich.panel import Panel

console = Console()


def main():
    console.print(Panel.fit(
        "[bold cyan]🤖 Бухгалтерский AI-ассистент[/bold cyan]\n"
        "Введите 'exit' для выхода",
        border_style="cyan"
    ))

    agent = AccountingAgent()

    while True:
        console.print("\n[bold green]Вопрос:[/bold green]", end=" ")
        query = input()

        if query.lower() in ['exit', 'quit', 'выход']:
            console.print("[yellow]До свидания![/yellow]")
            break

        if not query.strip():
            continue

        # Получаем ответ
        console.print("\n[cyan]Думаю...[/cyan]")
        result = agent.answer(query)

        # Выводим результат
        console.print(Panel(
            result['response'],
            title=f"[bold]Ответ ({result['query_type']})[/bold]",
            border_style="green"
        ))


if __name__ == '__main__':
    main()

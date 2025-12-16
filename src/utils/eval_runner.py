"""
Утилита для запуска evaluation pipeline
"""

import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import json

console = Console()


class EvalRunner:
    """Запускает полный цикл evaluation"""

    def __init__(self):
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)

    def run_all_evals(self):
        """
        Запускает все evaluation тесты последовательно
        """
        console.print(Panel.fit(
            "[bold cyan]🚀 Запуск полного цикла Evaluation[/bold cyan]\n"
            "Это займет несколько минут...",
            border_style="cyan"
        ))

        # Шаг 1: Проверка наличия тестовых данных
        console.print("\n[bold]Шаг 1:[/bold] Проверка тестовых данных...")
        data_file = Path('src/data/synthetic_conversations.json')

        if not data_file.exists():
            console.print("[yellow]⚠ Тестовые данные не найдены. Генерируем...[/yellow]")
            self._generate_test_data()
        else:
            console.print("[green]✓ Тестовые данные найдены[/green]")

        # Шаг 2: Запуск correctness тестов
        console.print("\n[bold]Шаг 2:[/bold] Запуск Correctness тестов...")
        correctness_success = self._run_pytest('src/evals/test_correctness.py')

        # Шаг 3: Запуск safety тестов
        console.print("\n[bold]Шаг 3:[/bold] Запуск Safety тестов...")
        safety_success = self._run_pytest('src/evals/test_safety.py')

        # Шаг 4: Генерация отчета
        console.print("\n[bold]Шаг 4:[/bold] Генерация итогового отчета...")
        self._generate_report()

        # Итоги
        console.print("\n" + "="*70)
        if correctness_success and safety_success:
            console.print("[bold green]✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО![/bold green]")
        else:
            console.print("[bold red]❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ[/bold red]")
            if not correctness_success:
                console.print("  [red]- Correctness тесты: FAILED[/red]")
            if not safety_success:
                console.print("  [red]- Safety тесты: FAILED[/red]")

        console.print("="*70 + "\n")

        return correctness_success and safety_success

    def _generate_test_data(self):
        """Генерирует тестовые данные"""
        from .data_generator import SyntheticDataGenerator

        generator = SyntheticDataGenerator()
        generator.generate_all(salary_count=20, vat_count=20)

    def _run_pytest(self, test_file: str) -> bool:
        """
        Запускает pytest для конкретного файла

        Returns:
            True если тесты прошли успешно
        """
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', test_file, '-v', '--tb=short'],
                capture_output=True,
                text=True
            )

            # Выводим stdout
            if result.stdout:
                print(result.stdout)

            # Проверяем успешность
            return result.returncode == 0

        except Exception as e:
            console.print(f"[red]Ошибка при запуске тестов: {e}[/red]")
            return False

    def _generate_report(self):
        """Генерирует итоговый отчет"""
        console.print("\n[cyan]Генерация markdown отчета...[/cyan]")

        # Собираем все результаты
        results = self._collect_all_results()

        # Создаем markdown отчет
        report_md = self._create_markdown_report(results)

        # Сохраняем markdown
        report_file = self.results_dir / 'report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_md)

        console.print(f"[green]✓ Отчет сохранен в {report_file}[/green]")

        # Выводим краткую статистику в консоль
        self._print_summary_table(results)

    def _collect_all_results(self) -> dict:
        """Собирает результаты из всех JSON файлов"""
        results = {
            'salary_correctness': [],
            'vat_correctness': [],
            'adversarial_safety': [],
            'edge_case_safety': []
        }

        # Загрузка результатов
        file_mapping = {
            'salary_correctness_results.json': 'salary_correctness',
            'vat_correctness_results.json': 'vat_correctness',
            'adversarial_safety_results.json': 'adversarial_safety',
            'edge_case_safety_results.json': 'edge_case_safety'
        }

        for filename, key in file_mapping.items():
            file_path = self.results_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    results[key] = json.load(f)

        return results

    def _create_markdown_report(self, results: dict) -> str:
        """Создает markdown отчет"""
        report = "# 📊 Evaluation Report: Accounting Agent\n\n"
        report += "## 📋 Общая информация\n\n"
        report += f"- **Модель агента**: {self._get_model_name()}\n"
        report += f"- **Модель evaluator**: {self._get_eval_model_name()}\n"
        report += f"- **Дата**: {self._get_current_date()}\n\n"

        # Correctness метрики
        report += "## ✅ Correctness Metrics\n\n"
        report += self._format_correctness_section(results)

        # Safety метрики
        report += "\n## 🛡️ Safety Metrics\n\n"
        report += self._format_safety_section(results)

        # Детальные результаты
        report += "\n## 📝 Детальные результаты\n\n"
        report += self._format_detailed_results(results)

        # Рекомендации
        report += "\n## 💡 Рекомендации по улучшению\n\n"
        report += self._generate_recommendations(results)

        return report

    def _format_correctness_section(self, results: dict) -> str:
        """Форматирует секцию Correctness"""
        section = "### Расчет заработной платы\n\n"

        salary_results = results.get('salary_correctness', [])
        if salary_results:
            total = len(salary_results)
            passed = sum(1 for r in salary_results if r['eval_result']['pass'])
            avg_score = sum(r['eval_result']['score'] for r in salary_results) / total if total > 0 else 0

            section += f"- **Всего тестов**: {total}\n"
            section += f"- **Пройдено**: {passed} ({passed/total*100:.1f}%)\n"
            section += f"- **Средний score**: {avg_score:.1f}/100\n\n"

        section += "### Консультации по НДС\n\n"

        vat_results = results.get('vat_correctness', [])
        if vat_results:
            total = len(vat_results)
            passed = sum(1 for r in vat_results if r['eval_result']['pass'])
            avg_score = sum(r['eval_result']['score'] for r in vat_results) / total if total > 0 else 0

            section += f"- **Всего тестов**: {total}\n"
            section += f"- **Пройдено**: {passed} ({passed/total*100:.1f}%)\n"
            section += f"- **Средний score**: {avg_score:.1f}/100\n\n"

        return section

    def _format_safety_section(self, results: dict) -> str:
        """Форматирует секцию Safety"""
        section = "### Adversarial тесты\n\n"

        adv_results = results.get('adversarial_safety', [])
        if adv_results:
            total = len(adv_results)
            passed = sum(1 for r in adv_results if r['eval_result']['pass'])
            critical = sum(1 for r in adv_results if r['eval_result'].get('severity') in ['high', 'critical'])

            section += f"- **Всего тестов**: {total}\n"
            section += f"- **Безопасно**: {passed} ({passed/total*100:.1f}%)\n"
            section += f"- **Критических провалов**: {critical}\n\n"

        section += "### Edge case тесты\n\n"

        edge_results = results.get('edge_case_safety', [])
        if edge_results:
            total = len(edge_results)
            passed = sum(1 for r in edge_results if r['eval_result']['pass'])

            section += f"- **Всего тестов**: {total}\n"
            section += f"- **Пройдено**: {passed} ({passed/total*100:.1f}%)\n\n"

        return section

    def _format_detailed_results(self, results: dict) -> str:
        """Форматирует детальные результаты"""
        section = "### Примеры провалов\n\n"

        # Собираем провальные тесты
        all_failures = []

        for category, items in results.items():
            for item in items:
                if not item.get('eval_result', {}).get('pass', True):
                    all_failures.append({
                        'category': category,
                        'item': item
                    })

        if all_failures:
            for failure in all_failures[:5]:  # Показываем первые 5
                item = failure['item']
                section += f"**{failure['category']}**\n\n"
                section += f"- Query: `{item.get('query') or item.get('user_message', 'N/A')}`\n"
                section += f"- Score: {item['eval_result']['score']}/100\n"
                section += f"- Critique: {item['eval_result'].get('critique', 'N/A')}\n\n"
        else:
            section += "*Нет провальных тестов*\n\n"

        return section

    def _generate_recommendations(self, results: dict) -> str:
        """Генерирует рекомендации"""
        recommendations = []

        # Анализ correctness
        salary_results = results.get('salary_correctness', [])
        if salary_results:
            avg_score = sum(r['eval_result']['score'] for r in salary_results) / len(salary_results)
            if avg_score < 80:
                recommendations.append("- Улучшить точность расчетов заработной платы")

        vat_results = results.get('vat_correctness', [])
        if vat_results:
            avg_score = sum(r['eval_result']['score'] for r in vat_results) / len(vat_results)
            if avg_score < 80:
                recommendations.append("- Улучшить качество консультаций по НДС")

        # Анализ safety
        adv_results = results.get('adversarial_safety', [])
        if adv_results:
            critical = sum(1 for r in adv_results if r['eval_result'].get('severity') in ['high', 'critical'])
            if critical > 0:
                recommendations.append("- **КРИТИЧНО**: Устранить уязвимости безопасности")

        if not recommendations:
            recommendations.append("- Отличная работа! Продолжайте в том же духе.")

        return "\n".join(recommendations) + "\n"

    def _print_summary_table(self, results: dict):
        """Выводит итоговую таблицу в консоль"""
        table = Table(title="📊 Итоговая статистика")

        table.add_column("Категория", style="cyan")
        table.add_column("Всего", justify="right")
        table.add_column("Пройдено", justify="right", style="green")
        table.add_column("Pass Rate", justify="right")
        table.add_column("Avg Score", justify="right")

        # Добавляем строки
        categories = [
            ('Salary Correctness', results.get('salary_correctness', [])),
            ('VAT Correctness', results.get('vat_correctness', [])),
            ('Adversarial Safety', results.get('adversarial_safety', [])),
            ('Edge Case Safety', results.get('edge_case_safety', []))
        ]

        for name, items in categories:
            if items:
                total = len(items)
                passed = sum(1 for r in items if r['eval_result']['pass'])
                pass_rate = (passed / total * 100) if total > 0 else 0
                avg_score = sum(r['eval_result']['score'] for r in items) / total if total > 0 else 0

                table.add_row(
                    name,
                    str(total),
                    str(passed),
                    f"{pass_rate:.1f}%",
                    f"{avg_score:.1f}"
                )

        console.print("\n")
        console.print(table)

    def _get_model_name(self) -> str:
        import os
        return os.getenv('AGENT_MODEL', 'gemini-2.0-flash-exp')

    def _get_eval_model_name(self) -> str:
        import os
        return os.getenv('EVAL_MODEL', 'gemini-2.0-flash-thinking-exp-1219')

    def _get_current_date(self) -> str:
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    runner = EvalRunner()
    success = runner.run_all_evals()

    sys.exit(0 if success else 1)

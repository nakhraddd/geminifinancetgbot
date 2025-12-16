"""
Тесты на правильность расчетов (Correctness)
"""

import json
import pytest
from pathlib import Path
from ..agent.agent import AccountingAgent
from .evaluator import GeminiEvaluator
from rich.console import Console

console = Console()


@pytest.fixture(scope="module")
def agent():
    """Фикстура для агента"""
    return AccountingAgent()


@pytest.fixture(scope="module")
def evaluator():
    """Фикстура для evaluator"""
    return GeminiEvaluator()


@pytest.fixture(scope="module")
def test_scenarios():
    """Загружает тестовые сценарии из JSON"""
    data_file = Path('src/data/synthetic_conversations.json')

    if not data_file.exists():
        pytest.skip("Файл synthetic_conversations.json не найден. Запустите сначала генератор данных.")

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


class TestSalaryCalculationCorrectness:
    """Тесты на правильность расчета зарплаты"""

    def test_salary_calculations(self, agent, evaluator, test_scenarios):
        """
        Проверяет правильность расчета зарплаты на всех сценариях
        """
        salary_scenarios = test_scenarios.get('salary_calculation', [])

        if not salary_scenarios:
            pytest.skip("Нет сценариев для тестирования зарплаты")

        results = []
        passed = 0
        failed = 0

        console.print(f"\n[bold cyan]Запуск тестов расчета зарплаты: {len(salary_scenarios)} сценариев[/bold cyan]\n")

        for scenario in salary_scenarios:
            scenario_id = scenario['id']
            user_message = scenario['user_message']

            console.print(f"[dim]Testing {scenario_id}:[/dim] {user_message[:60]}...")

            # Получаем ответ агента
            agent_result = agent.answer(user_message)
            agent_response = agent_result['response']

            # Оцениваем с помощью evaluator
            eval_result = evaluator.evaluate_salary_correctness(
                user_input=user_message,
                agent_response=agent_response,
                expected=scenario
            )

            # Сохраняем результат
            test_result = {
                'scenario_id': scenario_id,
                'user_message': user_message,
                'agent_response': agent_response,
                'eval_result': eval_result,
                'expected': scenario['expected_calculations']
            }
            results.append(test_result)

            # Подсчет статистики
            if eval_result['pass']:
                passed += 1
                console.print(f"  [green]✓ PASS[/green] (score: {eval_result['score']}/100)")
            else:
                failed += 1
                console.print(f"  [red]✗ FAIL[/red] (score: {eval_result['score']}/100)")
                console.print(f"  [yellow]Причина: {eval_result.get('critique', 'N/A')}[/yellow]")

        # Итоговая статистика
        total = len(salary_scenarios)
        pass_rate = (passed / total * 100) if total > 0 else 0

        console.print(f"\n[bold]Итоги тестов расчета зарплаты:[/bold]")
        console.print(f"  Всего: {total}")
        console.print(f"  [green]Пройдено: {passed}[/green]")
        console.print(f"  [red]Провалено: {failed}[/red]")
        console.print(f"  Pass rate: {pass_rate:.1f}%\n")

        # Сохраняем результаты
        self._save_results(results, 'salary_correctness_results.json')

        # Требуем минимум 70% успеха
        assert pass_rate >= 70, f"Pass rate {pass_rate:.1f}% ниже требуемых 70%"

    def _save_results(self, results, filename):
        """Сохраняет результаты тестов"""
        output_dir = Path('results')
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        console.print(f"[dim]Результаты сохранены в {output_file}[/dim]")


class TestVATConsultationCorrectness:
    """Тесты на правильность консультаций по НДС"""

    def test_vat_consultations(self, agent, evaluator, test_scenarios):
        """
        Проверяет правильность консультаций по НДС
        """
        vat_scenarios = test_scenarios.get('vat_consultation', [])

        if not vat_scenarios:
            pytest.skip("Нет сценариев для тестирования НДС")

        results = []
        passed = 0
        failed = 0

        console.print(f"\n[bold cyan]Запуск тестов консультаций по НДС: {len(vat_scenarios)} сценариев[/bold cyan]\n")

        for scenario in vat_scenarios:
            scenario_id = scenario['id']
            user_message = scenario['user_message']

            console.print(f"[dim]Testing {scenario_id}:[/dim] {user_message[:60]}...")

            # Получаем ответ агента
            agent_result = agent.answer(user_message)
            agent_response = agent_result['response']

            # Оцениваем с помощью evaluator
            eval_result = evaluator.evaluate_vat_correctness(
                user_input=user_message,
                agent_response=agent_response,
                expected=scenario
            )

            # Сохраняем результат
            test_result = {
                'scenario_id': scenario_id,
                'user_message': user_message,
                'agent_response': agent_response,
                'eval_result': eval_result,
                'expected': scenario['expected_answer']
            }
            results.append(test_result)

            # Подсчет статистики
            if eval_result['pass']:
                passed += 1
                console.print(f"  [green]✓ PASS[/green] (score: {eval_result['score']}/100)")
            else:
                failed += 1
                console.print(f"  [red]✗ FAIL[/red] (score: {eval_result['score']}/100)")
                console.print(f"  [yellow]Причина: {eval_result.get('critique', 'N/A')}[/yellow]")

        # Итоговая статистика
        total = len(vat_scenarios)
        pass_rate = (passed / total * 100) if total > 0 else 0

        console.print(f"\n[bold]Итоги тестов НДС консультаций:[/bold]")
        console.print(f"  Всего: {total}")
        console.print(f"  [green]Пройдено: {passed}[/green]")
        console.print(f"  [red]Провалено: {failed}[/red]")
        console.print(f"  Pass rate: {pass_rate:.1f}%\n")

        # Сохраняем результаты
        self._save_results(results, 'vat_correctness_results.json')

        # Требуем минимум 70% успеха
        assert pass_rate >= 70, f"Pass rate {pass_rate:.1f}% ниже требуемых 70%"

    def _save_results(self, results, filename):
        """Сохраняет результаты тестов"""
        output_dir = Path('results')
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        console.print(f"[dim]Результаты сохранены в {output_file}[/dim]")

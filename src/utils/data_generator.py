"""
Генератор синтетических тестовых данных с помощью Gemini
"""

import json
from typing import List, Dict
from pathlib import Path
from .gemini_client import get_agent_client
from rich.console import Console
from rich.progress import Progress

console = Console()

class SyntheticDataGenerator:
    """Генератор тестовых сценариев для eval"""

    def __init__(self):
        self.client = get_agent_client()
        self.output_dir = Path('src/data')
        self.output_dir.mkdir(exist_ok=True)

    def generate_salary_scenarios(self, count: int = 20) -> List[Dict]:
        """
        Генерирует тестовые сценарии расчета зарплаты

        Args:
            count: Количество сценариев для генерации

        Returns:
            Список сценариев в формате JSON
        """
        console.print(f"\n[cyan]Генерация {count} сценариев расчета зарплаты...[/cyan]")

        prompt = f"""
Создай {count} реалистичных тестовых сценариев для проверки расчета зарплаты в Казахстане.

ТРЕБОВАНИЯ К СЦЕНАРИЯМ:
1. Разнообразие зарплат: от 100,000 до 1,500,000 тенге
2. Разные формулировки вопросов (как реальные пользователи спрашивают)
3. Включить edge cases:
   - Зарплата ниже или равна МЗП (85,000)
   - Очень высокая зарплата (> 1,000,000)
   - С вычетами на иждивенцев (0-3 детей)
   - Неполная информация в вопросе
   - Опечатки в числах (300к вместо 300000)

4. Для каждого сценария рассчитай ПРАВИЛЬНЫЕ значения:
   - ОПВ = брутто × 0.10
   - ВОСМС = брутто × 0.02
   - Налогооблагаемый доход = брутто - ОПВ - 119,000 - (иждивенцы × 119,000)
   - ИПН = max(0, налогооблагаемый × 0.10)
   - Нетто = брутто - ОПВ - ВОСМС - ИПН

ФОРМАТ ВЫВОДА (строго JSON):
[
  {{
    "id": "salary_001",
    "user_message": "Рассчитай зарплату на руки при окладе 500000 тенге",
    "context": {{
      "gross_salary": 500000,
      "dependents": 0,
      "edge_case": null
    }},
    "expected_calculations": {{
      "opv": 50000,
      "vosms": 10000,
      "taxable_income": 331000,
      "ipn": 33100,
      "net_salary": 406900,
      "employer_so": 17500,
      "employer_sn": 45787
    }},
    "difficulty": "easy"
  }},
  ...
]

ПРИМЕРЫ ФОРМУЛИРОВОК:
- "Сколько получу на руки с окладом 450000?"
- "Зарплата 300к, двое детей, сколько налогов?"
- "Рассчитай нетто если брутто 750,000"
- "У меня оклад 250000 тенге, что останется после вычетов?"

Верни исключительно JSON массив, без дополнительного текста!
"""

        try:
            response = self.client.generate(prompt)
            scenarios = self._parse_json_response(response)

            # Валидация
            self._validate_salary_scenarios(scenarios)

            console.print(f"[green]✓[/green] Создано {len(scenarios)} сценариев зарплаты")
            return scenarios

        except Exception as e:
            console.print(f"[red]✗ Ошибка генерации: {e}[/red]")
            raise

    def generate_vat_scenarios(self, count: int = 20) -> List[Dict]:
        """
        Генерирует тестовые сценарии по НДС вычетам

        Args:
            count: Количество сценариев

        Returns:
            Список сценариев
        """
        console.print(f"\n[cyan]Генерация {count} сценариев НДС консультаций...[/cyan]")

        prompt = f"""
Создай {count} реалистичных сценариев для проверки консультаций по вычету НДС в Казахстане.

ТИПЫ РАСХОДОВ ДЛЯ СЦЕНАРИЕВ:
1. Аренда офиса (обычно можно)
2. Канцтовары (можно)
3. Компьютеры и оргтехника (можно)
4. Услуги связи (можно)
5. Представительские расходы (НЕЛЬЗЯ)
6. Корпоративные мероприятия (НЕЛЬЗЯ)
7. Личные расходы директора (НЕЛЬЗЯ)
8. ГСМ для служебного авто (можно при условиях)
9. Обучение сотрудников (можно)
10. Рекламные услуги (можно)

УСЛОВИЯ ВЫЧЕТА (по ст. 256 НК РК):
✅ МОЖНО если:
- Есть правильно оформленный ЭСФ
- Расход связан с облагаемой НДС деятельностью
- Товары/услуги получены

❌ НЕЛЬЗЯ если:
- Представительские расходы
- Личные нужды
- Безвозмездная передача
- Операции, не облагаемые НДС

ФОРМАТ ВЫВОДА (строго JSON):
[
  {{
    "id": "vat_001",
    "user_message": "Могу ли я принять НДС к вычету по аренде офиса?",
    "context": {{
      "expense_type": "office_rent",
      "has_esf": true,
      "amount_with_vat": 560000,
      "vat_amount": 60000
    }},
    "expected_answer": {{
      "can_deduct": true,
      "reasoning": "Аренда офиса - расход связанный с деятельностью, облагаемой НДС",
      "legal_reference": "Статья 256 НК РК",
      "required_docs": ["ЭСФ", "Договор аренды", "Акт приема-передачи"],
      "warnings": ["Убедитесь что арендодатель является плательщиком НДС"]
    }},
    "difficulty": "easy"
  }},
  {{
    "id": "vat_002",
    "user_message": "Оплатили корпоративное мероприятие с ЭСФ, вычет можно?",
    "context": {{
      "expense_type": "corporate_event",
      "has_esf": true,
      "amount_with_vat": 336000,
      "vat_amount": 36000
    }},
    "expected_answer": {{
      "can_deduct": false,
      "reasoning": "Корпоративные мероприятия относятся к представительским расходам",
      "legal_reference": "Статья 256 пункт 2 подпункт 1 НК РК",
      "required_docs": null,
      "warnings": ["НДС по представительским расходам не подлежит вычету даже при наличии ЭСФ"]
    }},
    "difficulty": "medium"
  }},
  ...
]

РАЗНООБРАЗИЕ ВОПРОСОВ:
- "Можно ли вычет НДС по [расход]?"
- "Купили [товар] с ЭСФ, примется ли НДС?"
- "Какие документы нужны для вычета НДС по [услуга]?"
- "Оплатили [расход], но без ЭСФ, что делать?"

Верни только JSON, без markdown разметки!
"""

        try:
            response = self.client.generate(prompt)
            scenarios = self._parse_json_response(response)

            # Валидация
            self._validate_vat_scenarios(scenarios)

            console.print(f"[green]✓[/green] Создано {len(scenarios)} сценариев НДС")
            return scenarios

        except Exception as e:
            console.print(f"[red]✗ Ошибка генерации: {e}[/red]")
            raise

    def _parse_json_response(self, response: str) -> List[Dict]:
        """Парсит JSON из ответа Gemini"""
        # Убираем markdown
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Не удалось распарсить JSON: {e}\n{response[:500]}")

    def _validate_salary_scenarios(self, scenarios: List[Dict]):
        """Проверяет корректность сценариев зарплаты"""
        for scenario in scenarios:
            assert 'id' in scenario, "Отсутствует 'id'"
            assert 'user_message' in scenario, "Отсутствует 'user_message'"
            assert 'expected_calculations' in scenario, "Отсутствует 'expected_calculations'"

            calc = scenario['expected_calculations']
            gross = scenario['context']['gross_salary']

            # Проверка ОПВ (с допустимой погрешностью из-за округления)
            expected_opv = gross * 0.10
            assert abs(calc['opv'] - expected_opv) < 1, f"Неверный ОПВ в {scenario['id']}: {calc['opv']} != {expected_opv}"

            # Проверка ВОСМС
            expected_vosms = gross * 0.02
            assert abs(calc['vosms'] - expected_vosms) < 1, f"Неверный ВОСМС в {scenario['id']}: {calc['vosms']} != {expected_vosms}"

    def _validate_vat_scenarios(self, scenarios: List[Dict]):
        """Проверяет корректность сценариев НДС"""
        for scenario in scenarios:
            assert 'id' in scenario, "Отсутствует 'id'"
            assert 'user_message' in scenario, "Отсутствует 'user_message'"
            assert 'expected_answer' in scenario, "Отсутствует 'expected_answer'"
            assert 'can_deduct' in scenario['expected_answer'], "Отсутствует 'can_deduct'"

    def save_scenarios(self, salary_scenarios: List[Dict], vat_scenarios: List[Dict]):
        """Сохраняет все сценарии в JSON файл"""
        all_data = {
            'salary_calculation': salary_scenarios,
            'vat_consultation': vat_scenarios,
            'metadata': {
                'total_scenarios': len(salary_scenarios) + len(vat_scenarios),
                'salary_count': len(salary_scenarios),
                'vat_count': len(vat_scenarios),
                'generated_at': str(Path.cwd())
            }
        }

        output_file = self.output_dir / 'synthetic_conversations.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        console.print(f"\n[green]✓ Данные сохранены в {output_file}[/green]")
        return output_file

    def generate_all(self, salary_count: int = 20, vat_count: int = 20):
        """Генерирует все тестовые данные"""
        console.print("\n[bold blue]🚀 Запуск генерации синтетических данных[/bold blue]")

        salary_scenarios = self.generate_salary_scenarios(salary_count)
        vat_scenarios = self.generate_vat_scenarios(vat_count)

        output_file = self.save_scenarios(salary_scenarios, vat_scenarios)

        console.print(f"\n[bold green]✅ Готово! Создано {salary_count + vat_count} тестовых сценариев[/bold green]")
        console.print(f"[dim]Файл: {output_file}[/dim]")

        return {
            'salary': salary_scenarios,
            'vat': vat_scenarios,
            'file': str(output_file)
        }


if __name__ == '__main__':
    generator = SyntheticDataGenerator()
    generator.generate_all(salary_count=20, vat_count=20)

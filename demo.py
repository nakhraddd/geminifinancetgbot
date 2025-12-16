#!/usr/bin/env python3
"""
Demo скрипт для демонстрации возможностей системы
Не требует установки зависимостей - просто показывает структуру
"""

print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🤖 Accounting Agent Evaluation Framework                     ║
║   ════════════════════════════════════════                     ║
║                                                                ║
║   Полноценная система AI Evals для бухгалтерского агента      ║
║   на базе Google Gemini API                                    ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

📋 ЧТО ВКЛЮЧЕНО:

✅ Accounting Agent
   └─ Специализация: Расчет зарплаты + консультации по НДС
   └─ Модель: Gemini 2.0 Flash
   └─ Промпты: Salary, VAT, General

✅ Gemini Evaluator
   └─ Correctness: Проверка правильности расчетов
   └─ Safety: Adversarial + edge case тесты
   └─ Модель: Gemini 2.0 Flash Thinking

✅ Synthetic Data Generator
   └─ 20 salary scenarios
   └─ 20 VAT consultation scenarios
   └─ Автоматический расчет expected values

✅ Test Suite (pytest)
   └─ test_correctness.py (40 тестов)
   └─ test_safety.py (8 тестов)
   └─ JSON результаты + Markdown отчет

═══════════════════════════════════════════════════════════════

🚀 БЫСТРЫЙ СТАРТ:

1️⃣  Установка (5 минут):
   $ ./setup.sh
   $ source venv/bin/activate
   $ python check_setup.py

2️⃣  Генерация тестовых данных:
   $ python generate_data.py

3️⃣  Интерактивное тестирование:
   $ python test_agent.py

4️⃣  Полный evaluation:
   $ python run_evals.py

═══════════════════════════════════════════════════════════════

💡 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:

┌─────────────────────────────────────────────────────────────┐
│ from src.agent.agent import AccountingAgent                 │
│                                                              │
│ agent = AccountingAgent()                                   │
│ result = agent.answer(                                      │
│     "Рассчитай зарплату на руки при окладе 500000 тенге"    │
│ )                                                            │
│                                                              │
│ print(result['response'])                                   │
│ # Выведет детальный расчет с ОПВ, ИПН, ВОСМС               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ from src.evals.evaluator import GeminiEvaluator             │
│                                                              │
│ evaluator = GeminiEvaluator()                               │
│ eval_result = evaluator.evaluate_salary_correctness(...)    │
│                                                              │
│ print(f"Pass: {eval_result['pass']}")                       │
│ print(f"Score: {eval_result['score']}/100")                 │
└─────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════

📊 METRICS & RESULTS:

После запуска run_evals.py в папке results/ появятся:

✓ salary_correctness_results.json
  └─ 20 тестов расчета зарплаты
  └─ Pass rate target: ≥70%

✓ vat_correctness_results.json
  └─ 20 тестов консультаций по НДС
  └─ Pass rate target: ≥70%

✓ adversarial_safety_results.json
  └─ 5 тестов на устойчивость к вредным запросам
  └─ Critical failures: должно быть 0

✓ edge_case_safety_results.json
  └─ 3 edge case теста
  └─ Pass rate target: ≥75%

✓ report.md
  └─ Итоговый markdown отчет с рекомендациями

═══════════════════════════════════════════════════════════════

🎯 JOBS TO BE DONE:

JTBD #1: Расчет заработной платы на руки
  👤 Персона: HR-менеджер, владелец бизнеса
  📈 Частота: Очень часто (каждый найм)
  ⚠️  Критичность: Высокая

  Success Criteria:
    ✓ Правильный ОПВ (10%)
    ✓ Правильный ИПН (с вычетами)
    ✓ Правильный ВОСМС (2%)
    ✓ Учет иждивенцев
    ✓ Обязательства работодателя (СО, СН)

JTBD #2: Определение права на вычет НДС
  👤 Персона: Бухгалтер, владелец бизнеса
  📈 Частота: Часто (крупные покупки)
  ⚠️  Критичность: Высокая (штрафы!)

  Success Criteria:
    ✓ Правильный вывод (можно/нельзя)
    ✓ Ссылка на НК РК
    ✓ Список документов
    ✓ Предупреждения о рисках
    ✓ Нет галлюцинаций

═══════════════════════════════════════════════════════════════

🏗️  АРХИТЕКТУРА:

┌──────────────┐         ┌──────────────┐
│ User Query   │────────▶│   Agent      │
└──────────────┘         │ (Gemini 2.0) │
                         └──────┬───────┘
                                │ Response
                                ▼
                         ┌──────────────┐
                         │  Evaluator   │
                         │ (Gemini 2.0) │
                         └──────┬───────┘
                                │ Evaluation
                                ▼
                         ┌──────────────┐
                         │   Results    │
                         │  + Report    │
                         └──────────────┘

═══════════════════════════════════════════════════════════════

📚 ДОКУМЕНТАЦИЯ:

📖 README.md          - Полная документация проекта
⚡ QUICKSTART.md      - Быстрый старт за 5 минут
🏗️  ARCHITECTURE.md    - Детальная архитектура
📊 PROJECT_SUMMARY.md - Краткое описание
🌳 TREE.txt           - Структура проекта

═══════════════════════════════════════════════════════════════

🔗 ПОЛЕЗНЫЕ КОМАНДЫ:

# Проверка установки
python check_setup.py

# Интерактивный режим
python test_agent.py

# Генерация данных
python generate_data.py

# Полный evaluation
python run_evals.py

# Запуск pytest тестов
pytest src/evals/ -v
pytest src/evals/test_correctness.py -v
pytest src/evals/test_safety.py -v

═══════════════════════════════════════════════════════════════

✨ СТАТУС: Production Ready ✅

Version: 1.0.0
Created: 2025-12-06
License: MIT

═══════════════════════════════════════════════════════════════

🎉 Готов к использованию! Начните с ./setup.sh

Для подробной информации смотрите README.md или QUICKSTART.md

═══════════════════════════════════════════════════════════════
""")

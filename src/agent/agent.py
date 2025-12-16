"""
Основной бухгалтерский AI-агент
"""

from typing import Optional
from ..utils.gemini_client import get_agent_client
from .prompts import (
    get_salary_calculation_prompt,
    get_vat_consultation_prompt,
    get_general_prompt
)

class AccountingAgent:
    """Бухгалтерский AI-ассистент на базе Google Gemini"""

    def __init__(self):
        self.client = get_agent_client()
        self.conversation_history = []

    def classify_query(self, user_query: str) -> str:
        """
        Определяет тип запроса пользователя

        Returns:
            'salary' | 'vat' | 'general'
        """
        query_lower = user_query.lower()

        # Ключевые слова для расчета зарплаты
        salary_keywords = ['зарплат', 'оклад', 'на руки', 'опв', 'ипн', 'восмс',
                          'получ', 'налог с зарплаты', 'удержан']

        # Ключевые слова для НДС
        vat_keywords = ['ндс', 'вычет', 'эсф', 'счет-фактур', 'принять к вычету']

        if any(kw in query_lower for kw in salary_keywords):
            return 'salary'
        elif any(kw in query_lower for kw in vat_keywords):
            return 'vat'
        else:
            return 'general'

    def answer(self, user_query: str) -> dict:
        """
        Отвечает на вопрос пользователя

        Returns:
            {
                'query': str,
                'response': str,
                'query_type': str,
                'model': str
            }
        """
        # Классификация запроса
        query_type = self.classify_query(user_query)

        # Выбор подходящего промпта
        if query_type == 'salary':
            prompt = get_salary_calculation_prompt(user_query)
        elif query_type == 'vat':
            prompt = get_vat_consultation_prompt(user_query)
        else:
            prompt = get_general_prompt(user_query)

        # Генерация ответа
        try:
            response = self.client.generate(prompt)

            # Сохранение в историю
            self.conversation_history.append({
                'user': user_query,
                'assistant': response,
                'type': query_type
            })

            return {
                'query': user_query,
                'response': response,
                'query_type': query_type,
                'model': self.client.model_name
            }

        except Exception as e:
            return {
                'query': user_query,
                'response': f"Ошибка при генерации ответа: {str(e)}",
                'query_type': query_type,
                'model': self.client.model_name,
                'error': str(e)
            }

    def reset_history(self):
        """Очистить историю разговора"""
        self.conversation_history = []

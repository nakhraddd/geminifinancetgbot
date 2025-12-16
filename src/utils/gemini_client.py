"""
Обертка для Google Gemini API
Единая точка для всех вызовов к Gemini
"""

import os
import google.generativeai as genai
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import json

load_dotenv()

class GeminiClient:
    """Клиент для работы с Google Gemini API"""

    def __init__(self,
                 model_name: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 2048):
        """
        Инициализация клиента

        Args:
            model_name: Название модели (по умолчанию из .env)
            temperature: Температура генерации (0.0-1.0)
            max_tokens: Максимальное количество токенов
        """
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")

        genai.configure(api_key=api_key)

        self.model_name = model_name or os.getenv('AGENT_MODEL', 'gemini-2.0-flash-exp')
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Инициализация модели
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                'temperature': self.temperature,
                'max_output_tokens': self.max_tokens,
            }
        )

    def generate(self, prompt: str) -> str:
        """
        Генерирует ответ от Gemini

        Args:
            prompt: Текст промпта

        Returns:
            Сгенерированный текст
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def generate_json(self, prompt: str) -> Dict[Any, Any]:
        """
        Генерирует JSON ответ от Gemini

        Args:
            prompt: Промпт с инструкцией вернуть JSON

        Returns:
            Распарсенный JSON объект
        """
        response_text = self.generate(prompt)

        # Очистка от markdown форматирования
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response_text}")

    def chat(self, messages: list) -> str:
        """
        Многоходовой диалог

        Args:
            messages: Список сообщений [{"role": "user", "content": "..."}, ...]

        Returns:
            Ответ модели
        """
        chat = self.model.start_chat(history=[])

        for msg in messages[:-1]:
            if msg['role'] == 'user':
                chat.send_message(msg['content'])

        # Последнее сообщение
        response = chat.send_message(messages[-1]['content'])
        return response.text


# Удобные фабрики
def get_agent_client() -> GeminiClient:
    """Возвращает клиент для основного агента"""
    return GeminiClient(
        model_name=os.getenv('AGENT_MODEL'),
        temperature=float(os.getenv('AGENT_TEMPERATURE', 0.7)),
        max_tokens=int(os.getenv('AGENT_MAX_TOKENS', 2048))
    )

def get_eval_client() -> GeminiClient:
    """Возвращает клиент для eval модели"""
    return GeminiClient(
        model_name=os.getenv('EVAL_MODEL'),
        temperature=float(os.getenv('EVAL_TEMPERATURE', 0.0)),
        max_tokens=int(os.getenv('EVAL_MAX_TOKENS', 4096))
    )

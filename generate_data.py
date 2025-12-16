#!/usr/bin/env python3
"""
Скрипт для генерации тестовых данных
"""

from src.utils.data_generator import SyntheticDataGenerator

if __name__ == '__main__':
    generator = SyntheticDataGenerator()
    generator.generate_all(salary_count=20, vat_count=20)

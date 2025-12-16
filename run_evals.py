#!/usr/bin/env python3
"""
Основной скрипт для запуска evaluation pipeline
"""

from src.utils.eval_runner import EvalRunner

if __name__ == '__main__':
    runner = EvalRunner()
    runner.run_all_evals()

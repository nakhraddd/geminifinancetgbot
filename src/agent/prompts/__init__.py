from ..base_prompts import (
    get_salary_calculation_prompt,
    get_vat_consultation_prompt,
    get_general_prompt,
)
from .antifraud_prompt import get_antifraud_prompt

__all__ = [
    "get_salary_calculation_prompt",
    "get_vat_consultation_prompt",
    "get_general_prompt",
    "get_antifraud_prompt",
]

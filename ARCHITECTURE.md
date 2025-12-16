# 🏗️ Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACCOUNTING AGENT EVAL SYSTEM                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│   User Input     │────────▶│  Accounting      │
│                  │         │     Agent        │
│ - Зарплата?      │         │                  │
│ - НДС вопрос?    │         │  (Gemini 2.0     │
│ - Бухучет?       │         │   Flash)         │
└──────────────────┘         └──────────────────┘
                                      │
                                      │ Response
                                      ▼
                             ┌──────────────────┐
                             │   Evaluator      │
                             │                  │
                             │  (Gemini 2.0     │
                             │   Thinking)      │
                             └──────────────────┘
                                      │
                                      │ Evaluation
                                      ▼
                             ┌──────────────────┐
                             │   Test Results   │
                             │                  │
                             │ - Correctness    │
                             │ - Safety         │
                             │ - Tone           │
                             └──────────────────┘
```

## Component Breakdown

### 1. Agent Layer (`src/agent/`)

```
AccountingAgent
├── config.py          → Domain config, JTBD, system prompt
├── prompts.py         → Task-specific prompts
│   ├── get_salary_calculation_prompt()
│   ├── get_vat_consultation_prompt()
│   └── get_general_prompt()
└── agent.py           → Main agent logic
    ├── classify_query()
    ├── answer()
    └── reset_history()
```

**Responsibilities:**
- Classify user queries (salary/vat/general)
- Select appropriate prompt
- Generate response via Gemini API
- Maintain conversation history

### 2. Evaluation Layer (`src/evals/`)

```
Evaluation System
├── evaluator.py                    → Gemini-based evaluator
│   ├── evaluate_salary_correctness()
│   ├── evaluate_vat_correctness()
│   └── evaluate_safety_and_tone()
├── test_correctness.py            → Pytest correctness tests
│   ├── TestSalaryCalculationCorrectness
│   └── TestVATConsultationCorrectness
└── test_safety.py                 → Pytest safety tests
    ├── TestAgentSafety.test_adversarial_resistance()
    └── TestAgentSafety.test_edge_case_handling()
```

**Responsibilities:**
- Evaluate agent responses for correctness
- Check safety and ethical compliance
- Generate detailed critiques and scores
- Detect hallucinations

### 3. Data Generation Layer (`src/utils/`)

```
Data Pipeline
├── data_generator.py
│   ├── generate_salary_scenarios()     → 20 test cases
│   └── generate_vat_scenarios()        → 20 test cases
└── synthetic_conversations.json        → Output
    ├── salary_calculation[]
    └── vat_consultation[]
```

**Responsibilities:**
- Generate realistic test scenarios
- Calculate expected values
- Validate scenario correctness
- Save to JSON format

### 4. Infrastructure Layer (`src/utils/`)

```
Infrastructure
├── gemini_client.py           → API wrapper
│   ├── GeminiClient
│   ├── get_agent_client()
│   └── get_eval_client()
└── eval_runner.py             → Orchestration
    ├── run_all_evals()
    ├── generate_report()
    └── collect_all_results()
```

**Responsibilities:**
- Manage Gemini API calls
- Orchestrate evaluation pipeline
- Generate reports
- Collect and aggregate results

## Data Flow

### Evaluation Pipeline Flow

```
1. DATA GENERATION
   └─▶ SyntheticDataGenerator
       └─▶ Gemini API (generate scenarios)
           └─▶ synthetic_conversations.json

2. AGENT EXECUTION
   └─▶ AccountingAgent.answer(query)
       └─▶ Gemini API (agent model)
           └─▶ agent_response

3. EVALUATION
   └─▶ GeminiEvaluator.evaluate_*()
       └─▶ Gemini API (eval model)
           └─▶ eval_result
               ├─ pass: bool
               ├─ score: 0-100
               ├─ errors: []
               └─ critique: str

4. REPORTING
   └─▶ EvalRunner.generate_report()
       └─▶ results/
           ├─ *_results.json
           └─ report.md
```

## Key Design Decisions

### 1. Gemini-Only Architecture

**Why:** Simplicity and consistency
- Single API provider
- Consistent response format
- Lower complexity vs. multi-provider setup

### 2. Two-Model Approach

**Agent Model:** `gemini-2.0-flash-exp`
- Fast, cost-effective
- Good for production use case
- Temperature: 0.7 for natural responses

**Eval Model:** `gemini-2.0-flash-thinking-exp-1219`
- More thorough reasoning
- Better at critique and analysis
- Temperature: 0.0 for deterministic evaluation

### 3. Domain-Specific JTBD

**Jobs To Be Done:**
1. **Salary Calculation** - HR managers, business owners
2. **VAT Consultation** - Accountants, business owners

Benefits:
- Clear success criteria
- Targeted test scenarios
- Measurable improvements

### 4. Multi-Dimensional Evaluation

**Correctness:**
- Mathematical accuracy
- Regulatory compliance
- Completeness of explanation

**Safety:**
- No illegal advice
- Appropriate caution
- Professional boundaries

**Tone:**
- Politeness
- Clarity
- User-friendliness

## Configuration

### Environment Variables

```bash
# Agent Config
AGENT_MODEL=gemini-2.0-flash-exp
AGENT_TEMPERATURE=0.7              # More creative
AGENT_MAX_TOKENS=2048

# Eval Config
EVAL_MODEL=gemini-2.0-flash-thinking-exp-1219
EVAL_TEMPERATURE=0.0               # Deterministic
EVAL_MAX_TOKENS=4096               # Longer analysis
```

### Prompts Structure

```
System Prompt (config.py)
├── Role definition
├── Responsibilities
├── Rules (do's and don'ts)
├── Актуальные данные (2025)
└── Format guidelines

Task Prompt (prompts.py)
├── Specific task instructions
├── Step-by-step calculation guide
├── Format requirements
└── Edge case handling
```

## Extensibility Points

### Adding New JTBD

1. Define in `src/agent/config.py`:
```python
JTBD_3_INVOICE_VERIFICATION = {
    "id": "jtbd_003",
    "name": "Проверка счета-фактуры",
    ...
}
```

2. Add prompt in `src/agent/prompts.py`:
```python
def get_invoice_verification_prompt(user_query: str) -> str:
    ...
```

3. Update classifier in `src/agent/agent.py`:
```python
def classify_query(self, user_query: str) -> str:
    ...
    elif 'счет-фактур' in query_lower:
        return 'invoice'
```

4. Add evaluator method in `src/evals/evaluator.py`:
```python
def evaluate_invoice_verification(self, ...):
    ...
```

5. Create test file `src/evals/test_invoice.py`

### Adding New Metrics

1. Add to evaluator:
```python
def evaluate_response_time(self, ...):
    ...
```

2. Update test files to call new metric

3. Update reporting in `eval_runner.py`

## Testing Strategy

### Unit Tests (future)
- Individual component testing
- Mock Gemini API responses
- Edge case validation

### Integration Tests (current)
- Full agent + evaluator pipeline
- Real API calls
- Synthetic data scenarios

### Safety Tests
- Adversarial queries
- Edge cases
- Ethical boundary testing

## Performance Considerations

### API Rate Limits
- Batch processing for large eval runs
- Exponential backoff on rate limits
- Caching where appropriate

### Cost Optimization
- Use Flash model for agent (cheaper)
- Use Thinking model only for eval (when needed)
- Limit token counts appropriately

### Evaluation Time
- ~40 test scenarios
- ~2-3 API calls per scenario
- Estimated time: 5-10 minutes

## Security & Privacy

### API Key Management
- Store in `.env` (never commit)
- Use environment variables
- Rotate keys regularly

### Data Privacy
- No real user data in synthetic scenarios
- Mock company names and amounts
- No PII in test cases

### Safety Guardrails
- Refuse illegal advice
- No legal consultation overreach
- Clear professional boundaries

---

**Last Updated:** 2025-12-06
**Version:** 1.0.0

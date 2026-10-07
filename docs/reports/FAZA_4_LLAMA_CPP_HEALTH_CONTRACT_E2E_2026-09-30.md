# Faza 4 — LlamaCppBackend: health-check, contract suite i E2E

Data: 2026-09-30

## Health-check
- runtime raportuje stan procesu przez `HealthCheckResult`;
- adapter sprawdza `/v1/models`.

## Contract suite
Zweryfikowano:
- zgodność z `TranslationBackend`;
- normal input;
- empty input;
- controlled HTTP error;
- incomplete result.

## E2E
Wykonano rzeczywisty przepływ:
`LlamaCppRuntimeManager → llama-server 0.4.0-dev → health → LlamaCppAdapter → translation → shutdown`.

Środowisko:
- executable: `/usr/local/bin/llama-server`;
- model: `Jan-v3.5-4B-Q4_K_XL/model.gguf`;
- CPU mode;
- port testowy: 18081.

Wynik:
- HEALTH=True;
- tłumaczenie wygenerowane przez model;
- LLAMA_CPP_E2E_OK;
- RUNTIME_RUNNING_AFTER_STOP=False.

## Weryfikacja końcowa Fazy 4
- pełny pytest V4: 77 passed;
- Ruff: PASS;
- mypy: PASS, 25 plików źródłowych.

Faza 4 spełnia bieżące kryterium: backend lokalny działa bez logiki backendowej w main.py.

# Faza 4 — LlamaCppBackend: adapter

Data: 2026-09-30

## Zakres
Dodano adapter lokalnego llama.cpp zgodny z portem TranslationBackend.

## Implementacja
- `src/tlumacz/backends/llama_cpp/adapter.py`;
- `LlamaCppConfig`;
- `LlamaCppAdapter.translate()`;
- `LlamaCppAdapter.health_check()`;
- transport stdlib `urllib`, bez zależności od GUI;
- endpoint OpenAI-compatible `/v1/chat/completions`;
- health endpoint `/v1/models`;
- jawna walidacja odpowiedzi i błędów HTTP/transportu.

## TDD i weryfikacja
- RED: brak modułu adaptera;
- GREEN: 3 testy adaptera;
- Ruff: PASS;
- mypy: PASS, 24 pliki źródłowe;
- pełny pytest V4: 61 passed.

## Granice
Adapter nie uruchamia ani nie zatrzymuje llama-server. Process ownership, runtime manager, timeout/cancellation lifecycle i E2E pozostają kolejnymi punktami Fazy 4.

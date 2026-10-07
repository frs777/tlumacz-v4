# Chunkowanie i tłumaczenie równoległe

## 1. ChunkPlanner

`ChunkPlanner` znajduje się w `src/tlumacz/application/chunk_planner.py`.

Jego odpowiedzialnością jest utworzenie planu chunków z jednostek przeznaczonych do tłumaczenia.

Chunk nie jest parserem formatu. Jest jednostką transportową dla warstwy tłumaczeniowej.

## 2. TranslationOrchestrator

`TranslationOrchestrator` łączy planowanie z wykonaniem. Jeżeli backend udostępnia `translate_batch`, orkiestrator może przekazać batch do wykonania.

Kontrakt przewiduje również kontrolowany fallback dla nieudanej próby batchowej.

## 3. TranslationExecutor

`TranslationExecutor` wykonuje pracę z ograniczoną współbieżnością przez `ThreadPoolExecutor(max_workers=...)`.

Wartość `max_workers` jest przekazywana z aplikacji. Kod GUI/aplikacji przekazuje konfigurację `parallel` jako `max_workers=max(1, parallel)`.

## 4. Batch a równoległość

To są dwa różne mechanizmy:

- batch — sposób przekazania wielu jednostek do backendu;
- równoległość — liczba prac wykonywanych współbieżnie przez executor.

Nie należy ich przedstawiać jako synonimów.

## 5. Integralność chunka

Aktualna architektura traktuje logiczny chunk jako jednostkę transakcyjną. Retry dotyczy całego nieudanego chunka, bez mieszania częściowych wyników z różnych prób.

Postęp chunka jest raportowany po przetworzeniu wszystkich jego jednostek.

## 6. llama.cpp

Adapter llama.cpp posiada `translate_batch()`, ale jego implementacja może wykonywać tłumaczenie jednostek indywidualnie. Dlatego obecność interfejsu batch nie oznacza automatycznie jednego wywołania modelu dla całego dokumentu.

## 7. Diagram

W diagramie głównym należy rozdzielić:

`ChunkPlanner` → `TranslationOrchestrator` → `TranslationExecutor` → backend.

Dzięki temu równoległość nie zostanie błędnie przypisana do filtra.

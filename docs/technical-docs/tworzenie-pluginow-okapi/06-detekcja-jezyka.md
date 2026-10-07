# Detekcja języka

## 1. Komponent

V4 posiada `src/tlumacz/language_detector.py`, oparty na Lingua.

Detekcja nie jest jednak globalnym parserem dokumentu. W ścieżce TranslateGemma dla llama.cpp źródło jest ustalane dla konkretnego requestu/chunku.

## 2. TranslateGemma

Dla `chat_template="translategemma"` adapter llama.cpp korzysta z `LlamaCppLanguageRouting` i detektora Lingua.

Modelowy przepływ:

`chunk/request → detekcja source → normalizacja source/target → prompt/chat template → llama.cpp`.

## 3. Ważne ograniczenie

TranslateGemma nie jest językiem. Jest trybem modelowym/backendowym.

Język docelowy pochodzi z konfiguracji tłumaczenia, natomiast wykrywanie źródła jest mechanizmem routingu tylko dla odpowiedniej ścieżki.

## 4. Cache

Wcześniejsze audyty V3/V4 potwierdzają, że wykryty język źródłowy jest również uwzględniany w kontekście cache dla tej ścieżki.

## 5. Apertium

Apertium ma własną strategię językową i mapowanie kodów ISO. Nie należy przedstawiać detekcji TranslateGemma jako wspólnego mechanizmu wszystkich backendów.

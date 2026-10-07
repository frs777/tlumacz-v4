# Help

> **Help status: 2026-10-05.** This guide describes the current **Translation**, **API & Server**, **Switches**, and **Help** tabs. When older project documentation differs from the running interface, use the current interface as the reference.

## Getting started

Tłumacz V4 translates documents without manual copy and paste.

### The shortest path

1. Open **Translation**.
2. Select the **Input file**.
3. Select the **Output file**, or keep the suggested name.
4. Select the **Target language**.
5. Open **API & Server** and choose the translation method.
6. If needed, configure **Switches**.
7. Click **Translate**.
8. Watch **Progress**, **Time**, **Speed**, **Log**, and **Translation preview**.

Click **Cancel** to stop the current translation. Cancellation is not the same as an error.

### Supported document formats

The active Filter Engine currently has filters for DOCX, ODT, HTML/XHTML, Markdown, EPUB, and XLIFF.

The system includes dedicated skills for **TXT** (`plaintext.md`) and **PDF** (`pdf.md`). The GUI exposes them and selects them automatically from the input file extension. Their presence as skills is separate from TXT/PDF registration in the active `FilterRegistry`.

### What happens after Translate

The application reads the document, selects translatable content, splits it into controlled pieces, prepares translation requests, runs the selected backend, validates results, reconstructs the document, and writes the output file.

## Translate a document

### Input and output files

**Input file** is the document you want to translate.

**Output file** is where the result is saved. After selecting the input file, the application can suggest a name containing the target-language code.

Use **Browse...** to select a file.

### Target language

For normal backends, select the language in **Target language**.

For Apertium, the Translation tab displays source and target languages in read-only fields. The current GUI does not provide a separate source-language selector on this tab.

### Progress and cancellation

**Progress** shows completion percentage.

**Time** shows the current operation time.

**Speed** shows current and average characters per second.

Click **Cancel** to stop the active operation. Check **Log** afterwards.

## Choose the translation method

Use **API & Server** to choose how the translation is performed.

### llama.cpp

**llama.cpp** performs translation locally with a model used by the managed llama.cpp server.

The section can contain:

- server URL;
- API key, if required;
- port;
- CPU or GPU computation mode;
- parallel tasks;
- GGUF model file;
- chat template;
- automatic server start;
- cache clearing after translation;
- restart after translation.

The available chat templates are **jinja**, **chatml**, and **TranslateGemma**.

**TranslateGemma is not a separate backend.** It is a special chat-template mode for llama.cpp.

**Restart server** applies to the llama.cpp server managed by the application. The restart keeps the current runtime configuration.

### Cloud

**Cloud** uses an external service over the network.

The current interface can expose profiles such as ChatGPT, Codex, Gemini Flash, Gemini Flash Lite, DeepSeek, Cohere, DeepL API Free, MyMemory, Microsoft Translator, DLX, and Mozhi.

Not every profile requires an API key. Never put a key from one service into another service's profile.

Text sent through Cloud leaves the computer and is processed by the selected service.

### Mozhi

Mozhi is a Cloud provider path.

You can select a specific instance or use automatic selection. You can also select an available translation engine.

### Apertium

**Apertium** is a local rule-based translation system. It is not an LLM.

The interface displays the detected or configured source and target language and information about the local Apertium setup.

A declared language pair is not proof that the complete runtime for that pair is ready. Check **Log** when a pair fails.

Apertium does not use the llama.cpp server lifecycle.

### Custom

**Custom** means a server running outside the application.

Tłumacz can connect to a compatible server, but it does not manage that server's process or model.

## Settings and tools

The **Switches** tab contains the glossary, skills, and LLM settings. Backend-specific behavior settings are shown with the corresponding backend in **API & Server**.

### Glossary

A glossary stores source and target terms.

1. Select a glossary file with **Browse...**.
2. Enter the source term.
3. Enter its target translation.
4. Click **Add**.

The interface also shows the number of stored term pairs.

### Skills

Skills provide additional translation instructions.

The application distinguishes **System skills** and **User skills**.

You can enable or disable skills. Available actions include **Import skill**, **New skill**, **Refresh**, and deleting a user skill.

**New skill** opens a template that you can edit and save.

The application can automatically select a base skill for the input file extension.

### LLM settings

This section is available for model-based translation paths and is hidden for Apertium.

**Block size** controls the maximum size of the text piece passed to translation.

**Temperature** affects how freely a model generates its answer. Lower values are more repeatable.

**Custom model instructions** add your own rules to the translation task.

**Skip patterns** define text patterns that should not be sent for translation.

### Save settings

Click **Save settings** to save the current settings.

Click **Restore defaults** to restore default values.

Changing the backend in **API & Server** is persisted by the active QML path. You do not need to restart the application only to switch backends.

## Results and problems

### Log

**Log** contains messages about the current operation.

When a translation fails, start with Log. Look for the backend, the error message, and the stage where processing stopped.

### Translation preview

**Translation preview** shows the result available after translation.

The preview does not have to look exactly like the document opened in an external editor, especially for formats with complex layout.

### Translation does not start

Check:

1. the input file exists;
2. the output location is writable;
3. the selected backend is correct;
4. the backend has the required settings;
5. Log contains the specific error.

### llama.cpp does not work

Check the GGUF file, address, port, computation mode, and chat template.

If the application manages the server, use **Restart server**.

### Cloud does not work

Check the profile, service address, API key if required, network access, and Log.

### Apertium does not work

Check the selected backend, displayed languages, available Apertium data, and Log.

Do not assume that a language-pair name in configuration means that the runtime is ready.

### The result is wrong

Do not immediately start another attempt.

First check Log, backend settings, glossary, enabled skills, and custom model instructions.

If the problem concerns document structure, test another supported format.

### Where to find technical details

The in-app help answers **"How do I use the program?"**.

Technical documentation describes implementation and project state.

Version **0.40.0** is a local Release Candidate. Open work includes Apertium, Windows, dependency/licensing closure, and full end-to-end TranslateGemma verification.

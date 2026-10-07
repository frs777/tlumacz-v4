# Procedura rollbacku 0.40.0

## Zasada główna
Rollback migracji wykonuje się przez powrót do **nienaruszonego V3**. Nie odtwarza się V3 przez częściowe kopiowanie plików z V4.

## Rollback instalacji V4
1. Zatrzymać używanie instalacji V4.
2. Zachować logi i artefakt V4 do analizy, jeżeli wystąpił błąd.
3. Usunąć lub odłączyć środowisko V4 zgodnie ze sposobem instalacji.
4. Przywrócić poprzedni sposób uruchamiania V3.
5. Zweryfikować działanie V3 na jego własnym drzewie.
6. Nie kopiować kodu V4 do katalogu V3.

## Konfiguracja użytkownika
Konfiguracja użytkownika ma osobny backup wykonywany przed migracją. Przy rollbacku przywraca się odpowiednią kopię konfiguracji, jeżeli zmiana konfiguracji jest przyczyną problemu.

## Artefakt release candidate
Aktualny wheel pozostaje w:
temp/wheel/tlumacz-0.40.0-py3-none-any.whl

SHA-256:
161d5667442b7dc9f1d90f85ed1e371ca57ca79530d690dfdd5d5e6914000835

## Ograniczenia
Procedura nie zakłada automatycznego downgrade'u w miejscu. V3 i V4 pozostają rozdzielone, co ogranicza ryzyko mieszania wersji.

---
id: plan-05-cloud-mozhi-2026-10-05
status: completed
meta:
  contentType: ModuleImplementationPlan
  category: plans
version: 1.0.0
updated: 2026-10-05
owner: platform-architecture
priority: P1
depends_on: [docs/Plany/PLAN-2026-10-05.md]
last_validation: "walidacja kodu, testy kontraktowe i live Mozhi 2026-10-06"
---
# PLAN-05 — Cloud i Mozhi

## 1. Oczekiwany rezultat
Utrzymać jeden router Cloud i izolowane providery bez mieszania transportu z core.

## 2. Zakres odpowiedzialności
CloudRouter; CloudProviderRegistry; OpenAI-compatible providers; DeepL; Microsoft; MyMemory; LibreTranslate; DLX; Mozhi; profile/keys/health.

## 3. Schemat budowy
```text
```text
CloudBackend
  ↓
CloudRouter
  ├─ provider registry
  ├─ standard providers
  ├─ MozhiProvider
  └─ Custom endpoint
          ↓
      ProviderResult
```
```

## 4. Połączenia z innymi modułami
Core nie zna URL/providerów. GUI zna tylko profile i capabilities. SecretStore dostarcza klucze.

## 5. Szczegółowy plan wdrożenia
1. Characterization provider contract.
2. Zweryfikować profile isolation.
3. Zweryfikować DLX i Custom.
4. Zweryfikować Mozhi discovery/engine mapping.
5. Oddzielić unit HTTP stubs od opcjonalnych live tests.
6. Dodać timeout/cancellation/error mapping.
7. Nie implementować automatycznego fallbacku.

## 6. Wymagania i zależności
Provider może być niedostępny bez uszkodzenia innych providerów. Sekret nie może być serializowany do profilu/settings.

## 7. Szczegóły integracji
Każdy provider implementuje wspólny rezultat. CloudRouter jest jedynym punktem wyboru. Custom nie staje się osobnym runtime.

## 8. Exit gate
Kontrakt providerów green; profile są izolowane; Mozhi pozostaje providerem; Custom działa przez router; brak wycieku sekretów; błędy nie powodują niejawnego routingu.

## 9. Zasady
Nie zmieniać innych modułów tylko po to, aby uprościć implementację tego modułu. Każda zmiana kontraktu wymaga aktualizacji testów, dokumentacji i głównego PLAN-2026-10-05.md.
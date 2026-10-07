# Faza 7 — HTML Filter prerekwizyt

Data: 2026-09-30

Dodano HtmlFilter jako prerekwizyt E2E Fazy 6.

Zakres:
- probe dla HTML/HTM/XHTML;
- deterministyczne text slots;
- wykluczenie script/style/head/meta/link/title;
- stabilne identyfikatory jednostek;
- hash źródła przed zapisem;
- zapis zachowujący DOCTYPE i markup.

Weryfikacja: 2 testy filtra; pełny suite 120 passed przed E2E i 122 po E2E.
"""Budowanie provider-neutralnych promptów tłumaczeniowych."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


class PromptBuilder:
    """Buduje system prompt, user prompt i kontekst chunka."""

    def __init__(self, *, target_language: str, system_prompt: str | None = None) -> None:
        self.target_language = target_language
        self._explicit_system_prompt = system_prompt

    def system_prompt(self) -> str:
        if self._explicit_system_prompt:
            return self._explicit_system_prompt
        return (
            "Jesteś profesjonalnym tłumaczem. "
            f"Przetłumacz CAŁY tekst na język {self.target_language}. "
            "Nie pomijaj, nie skracaj, nie streszczaj ani nie zmieniaj żadnej treści. "
            "Każde zdanie źródłowe musi mieć odpowiadające mu zdanie przetłumaczone. "
            "Zwróć TYLKO tłumaczenie — bez wyjaśnień, komentarzy ani notatek."
        )

    def user_prompt(self, text: str, *, format_name: str | None = None) -> str:
        if format_name:
            instruction = (
                f"Przetłumacz poniższy tekst na {self.target_language}, "
                f"zachowując formatowanie {format_name}:"
            )
        else:
            instruction = f"Przetłumacz poniższy tekst na {self.target_language}:"
        return f"{instruction}\n\n{text}"

    def context(self, units: Iterable[Any]) -> str:
        lines = ["KONTEKST BIEŻĄCEGO CHUNKA:"]
        for unit in units:
            if isinstance(unit, tuple) and len(unit) == 2:
                unit_id, source = unit
            else:
                unit_id, source = unit.id, unit.source
            lines.append(f"[{unit_id}] {source}")
        return "\n".join(lines)


__all__ = ["PromptBuilder"]

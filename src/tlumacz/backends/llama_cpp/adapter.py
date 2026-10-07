"""Adapter OpenAI-compatible dla lokalnego serwera llama.cpp.

Tryb translategemma jest specjalnym kontraktem wyłącznie dla modeli
TranslateGemma. Nie zmienia ścieżki standardowych modeli.
"""

from __future__ import annotations

import json
import logging
import re
import time
from collections.abc import Iterable
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from tlumacz.domain.contracts import BackendResult, HealthCheckResult
from tlumacz.language_detector import language_code_for, language_name_for

logger = logging.getLogger("tlumacz.backends.llama_cpp.adapter")


@dataclass(frozen=True, slots=True)
class LlamaCppConfig:
    """Konfiguracja transportu llama.cpp OpenAI-compatible API."""

    base_url: str = "http://127.0.0.1:18080/v1"
    api_key: str = "local"
    model: str = "local"
    # TranslateGemma 4B na CPU wymaga długiego czasu dla większych chunków.
    timeout: float = 1800.0
    temperature: float = 0.1
    chat_template: str = ""

    def __post_init__(self) -> None:
        if not self.base_url:
            raise ValueError("base_url nie może być puste")
        if not self.model:
            raise ValueError("model nie może być pusty")
        if self.timeout <= 0:
            raise ValueError("timeout musi być dodatni")
        if self.temperature < 0:
            raise ValueError("temperature nie może być ujemne")

    @property
    def normalized_base_url(self) -> str:
        return self.base_url.rstrip("/")


class LlamaCppAdapter:
    """Tłumaczy przez uruchomiony serwer llama.cpp."""

    def __init__(self, config: LlamaCppConfig) -> None:
        self.config = config

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
    ) -> BackendResult:
        if self.config.chat_template == "translategemma":
            return self._translate_translategemma(
                text, source_language=source_language, target_language=target_language
            )
        return self._translate_standard(
            text, source_language=source_language, target_language=target_language
        )

    def translate_batch(
        self,
        units: Iterable[tuple[str, str, str]],
        *,
        target_language: str,
    ) -> dict[str, BackendResult]:
        """Przetłumacz jeden logiczny chunk jednym requestem TranslateGemma.

        Batch korzysta z jawnych markerów segmentów. Są one kontraktem
        transportowym i muszą wrócić dokładnie raz w odpowiedzi modelu.
        """
        if self.config.chat_template != "translategemma":
            return self._translate_batch_individual(units, target_language=target_language)

        normalized = [(str(unit_id), str(text), str(source)) for unit_id, text, source in units]
        if not normalized:
            return {}
        target_code = language_code_for(target_language)
        if target_code == "auto":
            raise ValueError(f"Nieobsługiwany język docelowy TranslateGemma: {target_language!r}")

        source_codes = [language_code_for(source) for _, _, source in normalized]
        if any(code == "auto" for code in source_codes):
            raise ValueError("Batch TranslateGemma zawiera nieobsługiwany język źródłowy")
        if len(set(source_codes)) != 1:
            raise ValueError("Jeden batch TranslateGemma może zawierać tylko jeden język źródłowy")
        source_code = source_codes[0]

        source_name = language_name_for(source_code)
        target_name = language_name_for(target_code)
        sections = []
        for index, (_, text, _) in enumerate(normalized):
            sections.append(f"⟦TG_SEG_{index}⟧\n{text.strip()}")
        joined = "\n\n".join(sections)
        prompt = (
            "<start_of_turn>user\n"
            f"You are a professional {source_name} ({source_code}) to "
            f"{target_name} ({target_code}) translator. Translate every "
            "marked segment independently while preserving its meaning and "
            "formatting. Produce only the translations. Preserve every "
            "segment marker exactly once and never translate, rename, remove "
            "or duplicate a marker.\n\n"
            f"{joined}<end_of_turn>\n"
            "<start_of_turn>model\n"
        )
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "temperature": self.config.temperature,
            "max_tokens": 768,
        }
        response = self._request("/completions", payload, expected_status=200)
        translated = self._extract_completion_text(response)
        try:
            parts = self._parse_translategemma_batch(translated, len(normalized))
        except RuntimeError:
            payload["prompt"] = (
                prompt
                + "\n\nRETRY: poprzednia odpowiedź uszkodziła protokół segmentów. "
                "Zwróć ponownie wszystkie segmenty i zachowaj każdy marker "
                "⟦TG_SEG_N⟧ dokładnie raz, w tej samej kolejności. "
                "Nie dodawaj żadnego tekstu poza tłumaczeniami segmentów."
            )
            response = self._request("/completions", payload, expected_status=200)
            translated = self._extract_completion_text(response)
            parts = self._parse_translategemma_batch(translated, len(normalized))
        return {
            unit_id: BackendResult(
                text=parts[index],
                source_language=source_code,
                target_language=target_code,
                metadata={
                    "backend": "llama_cpp",
                    "model": self.config.model,
                    "chat_template": "translategemma",
                    "batch": True,
                    "batch_size": len(normalized),
                    "source_language_code": source_code,
                    "target_language_code": target_code,
                },
            )
            for index, (unit_id, _, _) in enumerate(normalized)
        }

    def _translate_batch_individual(
        self,
        units: Iterable[tuple[str, str, str]],
        *,
        target_language: str,
    ) -> dict[str, BackendResult]:
        return {
            unit_id: self.translate(
                text,
                source_language=source_language,
                target_language=target_language,
            )
            for unit_id, text, source_language in units
        }

    @staticmethod
    def _parse_translategemma_batch(text: str, expected_count: int) -> list[str]:
        marker = re.compile(r"⟦TG_SEG_(\d+)⟧")
        matches = list(marker.finditer(text))
        if len(matches) != expected_count:
            raise RuntimeError(
                "Odpowiedź TranslateGemma ma nieprawidłową liczbę markerów batcha"
            )
        indexes = [int(match.group(1)) for match in matches]
        if indexes != list(range(expected_count)):
            raise RuntimeError("Odpowiedź TranslateGemma ma brakujące, duplikowane lub przestawione segmenty")
        parts: list[str] = []
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            value = text[match.end():end].strip()
            if not value:
                raise RuntimeError(f"Odpowiedź TranslateGemma ma pusty segment {index}")
            parts.append(value)
        return parts

    def _translate_standard(
        self, text: str, *, source_language: str, target_language: str
    ) -> BackendResult:
        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Jesteś profesjonalnym tłumaczem. "
                        f"Przetłumacz tekst z języka {source_language} "
                        f"na język {target_language}. Zwróć wyłącznie tłumaczenie."
                    ),
                },
                {"role": "user", "content": text},
            ],
            "temperature": self.config.temperature,
        }
        response = self._request("/chat/completions", payload, expected_status=200)
        translated = self._extract_chat_content(response)
        return BackendResult(
            text=translated,
            source_language=source_language,
            target_language=target_language,
            metadata={"backend": "llama_cpp", "model": self.config.model},
        )

    def _translate_translategemma(
        self, text: str, *, source_language: str, target_language: str
    ) -> BackendResult:
        source_code = language_code_for(source_language)
        if source_code == "auto":
            raise ValueError(
                f"Nieobsługiwany język źródłowy TranslateGemma: {source_language!r}"
            )

        target_code = language_code_for(target_language)
        if target_code == "auto":
            raise ValueError(
                f"Nieobsługiwany język docelowy TranslateGemma: {target_language!r}"
            )

        prompt = self._build_translategemma_prompt(
            text,
            source_code=source_code,
            target_code=target_code,
        )
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "temperature": self.config.temperature,
            # TranslateGemma nie może dostać nieograniczonej generacji.
            # Bez limitu llama.cpp ustawia n_predict=-1 i może kontynuować
            # generowanie po utracie poprawnego stop tokenu, blokując GUI.
            "max_tokens": 768,
        }
        response = self._request("/completions", payload, expected_status=200)
        translated = self._extract_completion_text(response)
        return BackendResult(
            text=translated,
            source_language=source_code,
            target_language=target_code,
            metadata={
                "backend": "llama_cpp",
                "model": self.config.model,
                "chat_template": "translategemma",
                "source_language_code": source_code,
                "target_language_code": target_code,
                "endpoint": "/completions",
            },
        )

    @staticmethod
    def _build_translategemma_prompt(
        text: str, *, source_code: str, target_code: str
    ) -> str:
        source_name = language_name_for(source_code)
        target_name = language_name_for(target_code)
        return (
            "<start_of_turn>user\n"
            f"You are a professional {source_name} ({source_code}) to "
            f"{target_name} ({target_code}) translator. Your goal is to "
            f"accurately convey the meaning and nuances of the original "
            f"{source_name} text while adhering to {target_name} grammar, "
            f"vocabulary, and cultural sensitivities.\n"
            f"Produce only the {target_name} translation, without any "
            f"additional explanations or commentary. Please translate the "
            f"following {source_name} text into {target_name}:\n\n\n"
            f"{text.strip()}<end_of_turn>\n"
            "<start_of_turn>model\n"
        )

    @staticmethod
    def _extract_completion_text(response: dict[str, object]) -> str:
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("Nieprawidłowy format odpowiedzi llama.cpp")
        choice = choices[0]
        if not isinstance(choice, dict):
            raise RuntimeError("Nieprawidłowy format odpowiedzi llama.cpp")
        translated = choice.get("text")
        if not isinstance(translated, str):
            raise RuntimeError("Pole text odpowiedzi llama.cpp nie jest tekstem")
        return translated

    @staticmethod
    def _extract_chat_content(response: dict[str, object]) -> str:
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("Nieprawidłowy format odpowiedzi llama.cpp")
        choice = choices[0]
        if not isinstance(choice, dict):
            raise RuntimeError("Nieprawidłowy format odpowiedzi llama.cpp")
        message = choice.get("message")
        if not isinstance(message, dict):
            raise RuntimeError("Nieprawidłowy format odpowiedzi llama.cpp")
        translated = message.get("content")
        if not isinstance(translated, str):
            raise RuntimeError("Pole content odpowiedzi llama.cpp nie jest tekstem")
        return translated

    def health_check(self) -> HealthCheckResult:
        try:
            self._request("/models", None, expected_status=200)
        except Exception as exc:
            return HealthCheckResult.failed("llama_cpp", str(exc))
        return HealthCheckResult.ok("llama_cpp")

    def _request(
        self, path: str, payload: dict[str, object] | None, *, expected_status: int
    ) -> dict[str, object]:
        url = f"{self.config.normalized_base_url}/{path.lstrip('/')}"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        headers = {"Accept": "application/json"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        request = Request(
            url, data=data, headers=headers, method="POST" if data else "GET"
        )
        started = time.monotonic()
        logger.debug("Rozpoczęto żądanie llama.cpp: %s %s", request.method, url)
        try:
            with urlopen(request, timeout=self.config.timeout) as response:  # noqa: S310
                if response.status != expected_status:
                    raise RuntimeError(f"llama.cpp zwrócił HTTP {response.status}")
                decoded = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8", errors="replace")
            except OSError:
                pass
            closer = getattr(exc, "_closer", None)
            if closer is not None:
                closer.close()
            if exc.code == 503 and "Loading model" in detail:
                raise RuntimeError("llama.cpp nadal ładuje model; serwer nie jest jeszcze gotowy") from exc
            raise RuntimeError(f"llama.cpp zwrócił HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"Nie można połączyć z llama.cpp: {exc.reason}") from exc
        except TimeoutError as exc:
            raise RuntimeError("Timeout komunikacji z llama.cpp") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError("llama.cpp zwrócił nieprawidłowy JSON") from exc

        if not isinstance(decoded, dict):
            raise RuntimeError("llama.cpp zwrócił JSON inny niż obiekt")
        logger.debug("Zakończono żądanie llama.cpp: %s %s, czas %.3f s", request.method, url, time.monotonic() - started)
        return decoded


__all__ = ["LlamaCppAdapter", "LlamaCppConfig"]

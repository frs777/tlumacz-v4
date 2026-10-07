"""Providerzy Cloud odzyskani z kontraktu funkcjonalnego V3.

Warstwa transportowa pozostaje niezależna od Qt i GUI. Każdy provider zwraca
wspólny BackendResult i może zostać zarejestrowany w CloudRouter.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from tlumacz.domain.contracts import BackendResult

from .errors import CloudError, CloudErrorKind, classify_cloud_error
from .mozhi import MozhiProvider
from .provider import CloudProvider

logger = logging.getLogger("tlumacz.backends.cloud.providers")

CLOUD_PROVIDER_NAMES = (
    "openai",
    "deepl",
    "microsoft",
    "mymemory",
    "libretranslate",
    "mozhi",
    "dlx",
)


def _split_utf8(text: str, max_bytes: int) -> list[str]:
    """Podziel tekst tak, aby każdy fragment mieścił się w limicie bajtów UTF-8."""
    if max_bytes <= 0:
        raise ValueError("max_bytes musi być dodatni")
    result: list[str] = []
    current: list[str] = []
    current_bytes = 0
    for char in text:
        size = len(char.encode("utf-8"))
        if current and current_bytes + size > max_bytes:
            result.append("".join(current))
            current = []
            current_bytes = 0
        current.append(char)
        current_bytes += size
    if current:
        result.append("".join(current))
    return result or [""]


def _request_json(
    url: str,
    *,
    method: str = "GET",
    data: dict | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> dict | list:
    request_headers = {"Accept": "application/json"}
    if headers:
        request_headers.update(headers)
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    request = Request(url, data=body, headers=request_headers, method=method)
    started = time.monotonic()
    logger.debug("Rozpoczęto żądanie Cloud: %s %s", method, url)
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            detail = ""
        closer = getattr(exc, "_closer", None)
        if closer is not None:
            closer.close()
        raise RuntimeError(f"HTTP {exc.code}: {detail or exc.reason}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Błąd połączenia: {exc}") from exc
    try:
        result = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Provider zwrócił niepoprawny JSON.") from exc
    if not isinstance(result, (dict, list)):
        raise RuntimeError("Provider zwrócił nieoczekiwany format odpowiedzi.")
    logger.debug("Zakończono żądanie Cloud: %s %s, czas %.3f s", method, url, time.monotonic() - started)
    return result


def _result(text: str, source: str, target: str, provider: str, **metadata: object) -> BackendResult:
    return BackendResult(
        text=text,
        source_language=source,
        target_language=target,
        metadata={"backend": "cloud", "provider": provider, **metadata},
    )


class _BaseProvider:
    name = ""

    def _error(self, exc: Exception) -> CloudError:
        return classify_cloud_error(exc, provider=self.name)


class OpenAICompatibleProvider(_BaseProvider):
    name = "openai"

    def translate(self, text: str, *, source_language: str, target_language: str,
                  base_url: str, api_key: str, engine: str, timeout: float) -> BackendResult:
        endpoint = base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": engine,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Jesteś profesjonalnym tłumaczem. "
                        f"Przetłumacz tekst z języka {source_language} na język {target_language}. "
                        "Zwróć wyłącznie tłumaczenie."
                    ),
                },
                {"role": "user", "content": text},
            ],
        }
        try:
            response = _request_json(
                endpoint,
                method="POST",
                data=payload,
                headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
                timeout=timeout,
            )
            choices = response.get("choices") if isinstance(response, dict) else None
            message = choices[0].get("message") if isinstance(choices, list) and choices else None
            translated = message.get("content") if isinstance(message, dict) else None
            if not isinstance(translated, str) or not translated:
                raise RuntimeError("OpenAI-compatible zwrócił pusty wynik tłumaczenia.")
            return _result(translated, source_language, target_language, self.name, model=engine)
        except Exception as exc:
            raise self._error(exc) from exc


class DeepLProvider(_BaseProvider):
    name = "deepl"

    def translate(self, text: str, *, source_language: str, target_language: str,
                  base_url: str, api_key: str, engine: str, timeout: float) -> BackendResult:
        if not api_key:
            raise CloudError(
                "DeepL wymaga klucza API.",
                provider=self.name,
                kind=CloudErrorKind.AUTHENTICATION,
                retryable=False,
            )
        endpoint = base_url.rstrip("/")
        if not endpoint.endswith("/translate"):
            endpoint += "/translate"
        payload = {"text": [text], "target_lang": target_language.upper()}
        if source_language != "auto":
            payload["source_lang"] = source_language.lower()
        try:
            response = _request_json(
                endpoint,
                method="POST",
                data=payload,
                headers={"Authorization": f"DeepL-Auth-Key {api_key}"},
                timeout=timeout,
            )
            translations = response.get("translations") if isinstance(response, dict) else None
            translated = translations[0].get("text") if isinstance(translations, list) and translations else None
            if not isinstance(translated, str) or not translated:
                raise RuntimeError("DeepL zwrócił pusty wynik tłumaczenia.")
            return _result(translated, source_language, target_language, self.name)
        except CloudError:
            raise
        except Exception as exc:
            raise self._error(exc) from exc


class MicrosoftProvider(_BaseProvider):
    name = "microsoft"

    def translate(self, text: str, *, source_language: str, target_language: str,
                  base_url: str, api_key: str, engine: str, timeout: float) -> BackendResult:
        if not api_key:
            raise CloudError(
                "Microsoft Translator wymaga klucza API.",
                provider=self.name,
                kind=CloudErrorKind.AUTHENTICATION,
                retryable=False,
            )
        endpoint = base_url.rstrip("/") + "/translate?api-version=2026-06-06"
        payload = {"inputs": [{"text": text, **({"language": source_language} if source_language != "auto" else {}),
                               "targets": [{"language": target_language}]}]}
        try:
            response = _request_json(
                endpoint,
                method="POST",
                data=payload,
                headers={"Ocp-Apim-Subscription-Key": api_key},
                timeout=timeout,
            )
            values = response.get("value") if isinstance(response, dict) else None
            translations = values[0].get("translations") if isinstance(values, list) and values else None
            translated = translations[0].get("text") if isinstance(translations, list) and translations else None
            if not isinstance(translated, str) or not translated:
                raise RuntimeError("Microsoft Translator zwrócił pusty wynik tłumaczenia.")
            return _result(translated, source_language, target_language, self.name)
        except CloudError:
            raise
        except Exception as exc:
            raise self._error(exc) from exc


class MyMemoryProvider(_BaseProvider):
    name = "mymemory"

    def translate(self, text: str, *, source_language: str, target_language: str,
                  base_url: str, api_key: str, engine: str, timeout: float) -> BackendResult:
        parts: list[str] = []
        try:
            for part in _split_utf8(text, 500):
                params = {"q": part, "langpair": f"{source_language}|{target_language}", "mt": "1"}
                if api_key:
                    params["key"] = api_key
                response = _request_json(
                    f"{base_url}?{urlencode(params)}",
                    timeout=timeout,
                )
                status = response.get("responseStatus") if isinstance(response, dict) else None
                if status not in (None, 200, "200"):
                    detail = (
                        response.get("responseDetails", f"MyMemory responseStatus={status}")
                        if isinstance(response, dict)
                        else f"MyMemory responseStatus={status}"
                    )
                    raise RuntimeError(str(detail))
                data = response.get("responseData") if isinstance(response, dict) else None
                translated = data.get("translatedText") if isinstance(data, dict) else None
                if not isinstance(translated, str) or not translated:
                    raise RuntimeError("MyMemory zwrócił pusty wynik tłumaczenia.")
                parts.append(translated)
            return _result("".join(parts), source_language, target_language, self.name)
        except Exception as exc:
            raise self._error(exc) from exc


class LibreTranslateProvider(_BaseProvider):
    name = "libretranslate"

    def translate(self, text: str, *, source_language: str, target_language: str,
                  base_url: str, api_key: str, engine: str, timeout: float) -> BackendResult:
        endpoint = base_url.rstrip("/")
        if not endpoint.endswith("/translate"):
            endpoint += "/translate"
        payload = {"q": text, "source": source_language, "target": target_language, "format": "text"}
        if api_key:
            payload["api_key"] = api_key
        try:
            response = _request_json(endpoint, method="POST", data=payload, timeout=timeout)
            translated = response.get("translatedText") if isinstance(response, dict) else None
            if not isinstance(translated, str) or not translated:
                detail = (
                    response.get("error", "LibreTranslate zwrócił pusty wynik tłumaczenia.")
                    if isinstance(response, dict)
                    else "LibreTranslate zwrócił pusty wynik tłumaczenia."
                )
                raise RuntimeError(str(detail))
            return _result(translated, source_language, target_language, self.name)
        except Exception as exc:
            raise self._error(exc) from exc



class DLXProvider(_BaseProvider):
    name = "dlx"
    endpoint = "https://oneshot-free.www.deepl.com/v1/translate"
    max_text_length = 1500

    def translate(self, text: str, *, source_language: str, target_language: str,
                  base_url: str, api_key: str, engine: str, timeout: float) -> BackendResult:
        endpoint = base_url.rstrip("/") or self.endpoint
        if not endpoint.endswith("/translate"):
            endpoint += "/translate"
        parts = [text[i:i + self.max_text_length] for i in range(0, len(text), self.max_text_length)] or [""]
        translated_parts: list[str] = []
        instance_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        for part in parts:
            payload = {
                "text": [part],
                "target_lang": target_language.lower(),
                "usage_type": "translate",
                "app_information": {
                    "os": "ios",
                    "os_version": "26.0",
                    "app_version": "26.42",
                    "app_build": "5443737",
                    "instance_id": instance_id,
                },
            }
            if source_language != "auto":
                payload["source_lang"] = source_language.lower()
            try:
                response = _request_json(
                    endpoint,
                    method="POST",
                    data=payload,
                    headers={
                        "Authorization": "None",
                        "Accept": "*/*",
                        "Accept-Language": "en-US,en;q=0.9",
                        "User-Agent": "DeepL/26.42 CFNetwork/3826.600.41 Darwin/25.0.0",
                        "x-app-os-version": "26.0",
                        "x-app-instance-id": instance_id,
                        "x-app-session-id": session_id,
                    },
                    timeout=min(timeout, 20.0),
                )
                translations = response.get("translations") if isinstance(response, dict) else None
                translated = translations[0].get("text") if isinstance(translations, list) and translations else None
                if not isinstance(translated, str) or not translated:
                    raise RuntimeError("DLX zwrócił pusty wynik tłumaczenia.")
                translated_parts.append(translated)
            except Exception as exc:
                raise self._error(exc) from exc
        return _result("".join(translated_parts), source_language, target_language, self.name)


class CloudProviderRegistry:
    """Rejestr wszystkich aktywnych providerów odziedziczonych funkcjonalnie z V3."""

    def __init__(self, providers: tuple[CloudProvider, ...]) -> None:
        self._providers = {provider.name: provider for provider in providers}

    @classmethod
    def default(cls) -> CloudProviderRegistry:
        return cls((
            OpenAICompatibleProvider(),
            DeepLProvider(),
            MicrosoftProvider(),
            MyMemoryProvider(),
            LibreTranslateProvider(),
            MozhiProvider(),
            DLXProvider(),
        ))

    def get(self, name: str) -> CloudProvider:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise ValueError(f"Nieznany provider Cloud: {name!r}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._providers)

    def providers(self) -> tuple[CloudProvider, ...]:
        """Zwróć zarejestrowane adaptery bez ujawniania mapy wewnętrznej."""
        return tuple(self._providers.values())


__all__ = [
    "CLOUD_PROVIDER_NAMES",
    "CloudProviderRegistry",
    "DLXProvider",
    "DeepLProvider",
    "LibreTranslateProvider",
    "MicrosoftProvider",
    "MyMemoryProvider",
    "OpenAICompatibleProvider",
    "_split_utf8",
]

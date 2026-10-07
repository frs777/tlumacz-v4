"""Mozhi cloud provider adapter."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from tlumacz.domain.contracts import BackendResult

from .errors import CloudErrorKind, classify_cloud_error
from .provider import CloudProvider

DEFAULT_MOZHI_INSTANCE = "https://mozhi.ducks.party"
MOZHI_ENGINE_API_IDS = {
    "duckduckgo": "duckduckgo",
    "google": "google",
    "deepl": "deepl",
    "yandex": "yandex",
    "reverso": "reverso",
    "mymemory": "mymemory",
}
MOZHI_ENGINES = (
    ("DuckDuckGo", "duckduckgo"),
    ("Google", "google"),
    ("DeepL", "deepl"),
    ("Yandex", "yandex"),
    ("Reverso", "reverso"),
    ("MyMemory", "mymemory"),
)

MOZHI_INSTANCES = (
    "https://mozhi.aryak.me",
    "https://translate.bus-hit.me",
    "https://nyc1.mz.ggtyler.dev",
    "https://translate.projectsegfau.lt",
    "https://translate.nerdvpn.de",
    "https://mozhi.ducks.party",
    "https://mozhi.frontendfriendly.xyz",
    "https://mozhi.pussthecat.org",
    "https://mo.zorby.top",
    "https://mozhi.adminforge.de",
    "https://translate.privacyredirect.com",
    "https://mozhi.canine.tools",
    "https://mozhi.gitro.xyz",
)


SelectInstance = Callable[[str, float], str]


class MozhiProvider:
    """CloudProvider adapter for the Mozhi API."""

    name = "mozhi"

    def __init__(self, *, select_instance: SelectInstance | None = None) -> None:
        self._select_instance = select_instance or _select_fastest_instance

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
        base_url: str,
        api_key: str,
        engine: str,
        timeout: float,
    ) -> BackendResult:
        del api_key
        instance = self.select_instance(base_url, engine, min(timeout, 5.0))
        source = _normalize_language(engine, source_language)
        target = _normalize_language(engine, target_language)
        params = urlencode(
            {
                "engine": engine,
                "from": source,
                "to": target,
                "text": text,
            }
        )
        request = Request(
            f"{instance.rstrip('/')}/api/translate?{params}",
            headers={"Accept": "application/json"},
        )
        try:
            with urlopen(request, timeout=timeout) as response:  # noqa: S310
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError) as exc:
            raise classify_cloud_error(exc, provider=self.name) from exc
        except OSError as exc:
            raise classify_cloud_error(exc, provider=self.name) from exc
        except json.JSONDecodeError as exc:
            raise classify_cloud_error(
                exc,
                provider=self.name,
                kind=CloudErrorKind.INVALID_RESPONSE,
            ) from exc

        translated = _extract_translation(payload)
        if not translated:
            raise classify_cloud_error(
                RuntimeError(f"Mozhi: silnik {engine} zwrócił pusty wynik tłumaczenia."),
                provider=self.name,
                kind=CloudErrorKind.INVALID_RESPONSE,
            )

        return BackendResult(
            text=translated,
            source_language=source_language,
            target_language=target_language,
            metadata={
                "backend": "cloud",
                "provider": "mozhi",
                "engine": engine,
                "base_url": instance,
            },
        )

    def select_instance(
        self,
        base_url: str,
        engine: str,
        timeout: float,
    ) -> str:
        if base_url.strip().lower() != "auto":
            return _normalize_instance(base_url)
        return self._select_instance(engine, timeout)


def _extract_translation(payload: object) -> str:
    if isinstance(payload, dict):
        value = payload.get("translated-text")
        return value if isinstance(value, str) else ""
    if isinstance(payload, list):
        values = [
            item.get("translated-text")
            for item in payload
            if isinstance(item, dict)
        ]
        return "\n\n".join(value for value in values if isinstance(value, str) and value)
    return ""


def _normalize_instance(value: str) -> str:
    url = value.strip() or DEFAULT_MOZHI_INSTANCE
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url.rstrip("/")


def _normalize_language(engine: str, language: str) -> str:
    if engine != "mymemory":
        return language
    return {
        "de": "de-DE",
        "en": "en-US",
        "es": "es-ES",
        "fr": "fr-FR",
        "it": "it-IT",
        "pt": "pt-PT",
    }.get(language, language)


def _probe_instance(instance: str, engine: str, timeout: float) -> float | None:
    start = time.monotonic()
    base = _normalize_instance(instance)
    try:
        with urlopen(
            Request(f"{base}/api/engines", headers={"Accept": "application/json"}),
            timeout=timeout,
        ) as response:  # noqa: S310
            engines = json.loads(response.read().decode("utf-8"))
        if not isinstance(engines, dict) or engine not in engines:
            return None

        query = urlencode({"engine": engine})
        for endpoint in ("source_languages", "target_languages"):
            with urlopen(
                Request(
                    f"{base}/api/{endpoint}?{query}",
                    headers={"Accept": "application/json"},
                ),
                timeout=timeout,
            ) as response:  # noqa: S310
                languages = json.loads(response.read().decode("utf-8"))
            if not isinstance(languages, list) or not languages:
                return None

        return time.monotonic() - start
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, TypeError):
        return None


def _select_fastest_instance(engine: str, timeout: float) -> str:
    results: dict[str, float] = {}
    with ThreadPoolExecutor(max_workers=min(8, len(MOZHI_INSTANCES))) as executor:
        futures = {
            executor.submit(_probe_instance, instance, engine, timeout): instance
            for instance in MOZHI_INSTANCES
        }
        for future in as_completed(futures):
            try:
                elapsed = future.result()
            except Exception:  # pragma: no cover - defensive worker boundary
                elapsed = None
            if elapsed is not None and elapsed <= timeout:
                results[futures[future]] = elapsed

    if not results:
        return DEFAULT_MOZHI_INSTANCE
    return min(results, key=lambda item: results[item])


assert isinstance(MozhiProvider(), CloudProvider)


__all__ = ["DEFAULT_MOZHI_INSTANCE", "MOZHI_INSTANCES", "MOZHI_ENGINE_API_IDS", "MOZHI_ENGINES", "MozhiProvider"]

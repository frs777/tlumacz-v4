"""Cooperative cancellation primitives."""


from dataclasses import dataclass, field

from tlumacz.domain.errors import TranslationCancelledError


@dataclass(slots=True)
class CancellationToken:
    """Small synchronous token suitable for application and worker boundaries."""

    _cancelled: bool = field(default=False, init=False)

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    def cancel(self) -> None:
        self._cancelled = True

    def raise_if_cancelled(self) -> None:
        if self._cancelled:
            raise TranslationCancelledError("Translation was cancelled.")

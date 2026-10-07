"""Shared error taxonomy for cloud translation providers."""

from __future__ import annotations

from enum import StrEnum
from urllib.error import HTTPError, URLError


class CloudErrorKind(StrEnum):
    """Stable classification consumed by application/UI layers."""

    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    NETWORK = "network"
    HTTP = "http"
    INVALID_RESPONSE = "invalid_response"
    PROVIDER = "provider"
    UNKNOWN = "unknown"


class CloudError(RuntimeError):
    """Normalized cloud-provider failure."""

    def __init__(
        self,
        message: str,
        *,
        provider: str,
        kind: CloudErrorKind,
        retryable: bool,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.kind = kind
        self.retryable = retryable
        self.status_code = status_code


def classify_cloud_error(
    error: BaseException,
    *,
    provider: str,
    kind: CloudErrorKind | None = None,
) -> CloudError:
    """Map transport/HTTP exceptions into the shared cloud taxonomy."""

    if isinstance(error, CloudError):
        return error

    if kind is not None:
        return CloudError(
            str(error),
            provider=provider,
            kind=kind,
            retryable=kind in {
                CloudErrorKind.RATE_LIMIT,
                CloudErrorKind.TIMEOUT,
                CloudErrorKind.NETWORK,
            },
        )

    if isinstance(error, TimeoutError):
        return CloudError(
            str(error),
            provider=provider,
            kind=CloudErrorKind.TIMEOUT,
            retryable=True,
        )

    if isinstance(error, HTTPError):
        status = error.code
        if status in {401, 403}:
            error_kind = CloudErrorKind.AUTHENTICATION
            retryable = False
        elif status == 429:
            error_kind = CloudErrorKind.RATE_LIMIT
            retryable = True
        elif status == 408 or status >= 500:
            error_kind = CloudErrorKind.HTTP
            retryable = True
        else:
            error_kind = CloudErrorKind.HTTP
            retryable = False
        return CloudError(
            str(error),
            provider=provider,
            kind=error_kind,
            retryable=retryable,
            status_code=status,
        )

    if isinstance(error, URLError):
        return CloudError(
            str(error),
            provider=provider,
            kind=CloudErrorKind.NETWORK,
            retryable=True,
        )

    return CloudError(
        str(error),
        provider=provider,
        kind=CloudErrorKind.UNKNOWN,
        retryable=False,
    )


__all__ = ["CloudError", "CloudErrorKind", "classify_cloud_error"]

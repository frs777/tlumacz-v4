"""Domain errors shared by V4 contracts."""


class ContractError(Exception):
    """Base error for violated V4 domain contracts."""


class BackendError(ContractError):
    """Backend operation failed."""


class DocumentError(ContractError):
    """Document operation failed."""


class FilterError(ContractError):
    """Filter operation failed."""


class TranslationCancelledError(ContractError):
    """Translation was cooperatively cancelled."""

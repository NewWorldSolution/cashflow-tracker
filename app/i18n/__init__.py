from app.i18n import en

_LOCALE_MAP = {
    "en": en,
}

DEFAULT_LOCALE = "pl"


def get_messages(locale: str) -> dict:
    """Return the MESSAGES dict for the given locale, fallback to English."""
    module = _LOCALE_MAP.get(locale, en)
    return module.MESSAGES


def translate(key: str, locale: str) -> str:
    """Look up a UI string. Fallback to English if missing, then to key itself."""
    module = _LOCALE_MAP.get(locale, en)
    return module.MESSAGES.get(key, en.MESSAGES.get(key, key))


def translate_error(error: str, locale: str) -> str:
    """Translate a validation error string. Fallback to English (original)."""
    module = _LOCALE_MAP.get(locale, en)
    return module.VALIDATION_ERRORS.get(error, error)

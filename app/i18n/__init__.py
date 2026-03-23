from app.i18n import en, pl

_LOCALE_MAP = {
    "en": en,
    "pl": pl,
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


def format_date(value, locale: str) -> str:
    """Format a date value for display.

    Polish: DD.MM.YYYY  (e.g. 23.03.2026)
    English: pass-through (YYYY-MM-DD from DB or strftime result)
    """
    if not value:
        return "—"
    if locale == "pl":
        if hasattr(value, "strftime"):
            return value.strftime("%d.%m.%Y")
        parts = str(value).split("-")
        if len(parts) == 3:
            return f"{parts[2]}.{parts[1]}.{parts[0]}"
    return str(value)


def format_amount(value, locale: str) -> str:
    """Format a numeric amount for display.

    Polish: 1 234,56  (space as thousands sep, comma as decimal)
    English: 1,234.56
    """
    if value is None:
        return "—"
    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)
    if locale == "pl":
        formatted = f"{num:,.2f}"
        # swap: comma→placeholder, period→comma, placeholder→non-breaking space
        formatted = formatted.replace(",", "\x00").replace(".", ",").replace("\x00", "\u00a0")
        return formatted
    return f"{num:,.2f}"

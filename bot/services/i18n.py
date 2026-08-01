import json
from pathlib import Path

_LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
_SUPPORTED = ("ru", "en")
_FALLBACK = "ru"

_translations: dict[str, dict[str, str]] = {}


def _load() -> None:
    for lang in _SUPPORTED:
        path = _LOCALES_DIR / f"{lang}.json"
        with path.open(encoding="utf-8") as f:
            _translations[lang] = json.load(f)


_load()


def t(key: str, lang: str, **kwargs) -> str:
    lang = lang if lang in _translations else _FALLBACK
    template = _translations[lang].get(key) or _translations[_FALLBACK].get(key) or key
    return template.format(**kwargs) if kwargs else template


def available_languages() -> tuple[str, ...]:
    return _SUPPORTED


def translations() -> dict[str, dict[str, str]]:
    return _translations

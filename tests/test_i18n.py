from bot.services.i18n import available_languages, t, translations


def test_ru_and_en_have_the_same_keys():
    data = translations()
    assert set(data["ru"].keys()) == set(data["en"].keys())


def test_t_formats_placeholders():
    text = t("checkin.saved", "ru", score=8, streak=3, avg7="7.0")
    assert "8/10" in text
    assert "3 дн." in text


def test_t_falls_back_to_default_language_for_unknown_lang():
    assert t("common.back", "fr") == t("common.back", "ru")


def test_available_languages_contains_ru_and_en():
    assert set(available_languages()) == {"ru", "en"}

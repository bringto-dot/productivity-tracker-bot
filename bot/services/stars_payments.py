from aiogram.types import LabeledPrice

CURRENCY = "XTR"
_PAYLOAD_PREFIX = "sub_plan_"


def build_prices(stars_price: int) -> list[LabeledPrice]:
    return [LabeledPrice(label="Subscription", amount=stars_price)]


def build_payload(plan_id: int) -> str:
    return f"{_PAYLOAD_PREFIX}{plan_id}"


def parse_payload(payload: str) -> int | None:
    if not payload.startswith(_PAYLOAD_PREFIX):
        return None
    try:
        return int(payload[len(_PAYLOAD_PREFIX):])
    except ValueError:
        return None

from datetime import date, timedelta


def current_streak(distinct_dates: list[date], today: date) -> int:
    if not distinct_dates:
        return 0
    dates_set = set(distinct_dates)
    if today in dates_set:
        cursor = today
    elif (today - timedelta(days=1)) in dates_set:
        cursor = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    while cursor in dates_set:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def best_streak(distinct_dates: list[date]) -> int:
    if not distinct_dates:
        return 0
    ordered = sorted(set(distinct_dates))
    best = 1
    current = 1
    for i in range(1, len(ordered)):
        if ordered[i] - ordered[i - 1] == timedelta(days=1):
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def average(scores: list[int]) -> float | None:
    if not scores:
        return None
    return sum(scores) / len(scores)


def format_average(value: float | None) -> str:
    return f"{value:.1f}" if value is not None else "—"

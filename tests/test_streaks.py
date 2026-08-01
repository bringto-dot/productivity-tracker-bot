from datetime import date, timedelta

from bot.services import streaks


def _d(days_ago: int, today: date) -> date:
    return today - timedelta(days=days_ago)


def test_current_streak_counts_consecutive_days_ending_today():
    today = date(2026, 8, 1)
    dates = [_d(0, today), _d(1, today), _d(2, today), _d(5, today)]
    assert streaks.current_streak(dates, today) == 3


def test_current_streak_allows_grace_if_not_checked_in_today_yet():
    today = date(2026, 8, 1)
    dates = [_d(1, today), _d(2, today), _d(3, today)]
    assert streaks.current_streak(dates, today) == 3


def test_current_streak_zero_when_gap_before_today():
    today = date(2026, 8, 1)
    dates = [_d(2, today), _d(3, today)]
    assert streaks.current_streak(dates, today) == 0


def test_current_streak_empty():
    assert streaks.current_streak([], date(2026, 8, 1)) == 0


def test_best_streak_finds_longest_run():
    today = date(2026, 8, 1)
    dates = [
        _d(0, today),
        _d(1, today),
        _d(2, today),
        _d(10, today),
        _d(11, today),
        _d(12, today),
        _d(13, today),
    ]
    assert streaks.best_streak(dates) == 4


def test_best_streak_empty():
    assert streaks.best_streak([]) == 0


def test_average_and_format():
    assert streaks.average([]) is None
    assert streaks.format_average(None) == "—"
    assert streaks.average([5, 7, 6]) == 6.0
    assert streaks.format_average(6.0) == "6.0"

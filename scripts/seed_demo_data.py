from pathlib import Path

from bot.database.engine import async_session_maker
from bot.database.models import GuideCategory
from bot.database.repo import guides as guides_repo
from bot.database.repo import plans as plans_repo

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_guides"

_DEMO_GUIDES = [
    {
        "title": "5 техник тайм-менеджмента",
        "description": "Помодоро, матрица Эйзенхауэра, тайм-блокинг и другие рабочие методы.",
        "category": GuideCategory.GUIDE,
        "file": "time_management_guide.pdf",
        "is_premium": False,
    },
    {
        "title": "Утренняя зарядка на 15 минут",
        "description": "Короткая тренировка без спортзала: разминка, основной блок, заминка.",
        "category": GuideCategory.TRAINING,
        "file": "morning_workout.pdf",
        "is_premium": False,
    },
    {
        "title": "Мини-лекция: как формируются привычки",
        "description": "Петля привычки, наслоение привычек и почему миф про 21 день не работает.",
        "category": GuideCategory.LECTURE,
        "file": "habits_lecture.pdf",
        "is_premium": True,
    },
]

_DEMO_PLANS = [
    {"title": "Неделя", "days": 7, "stars_price": 49},
    {"title": "Месяц", "days": 30, "stars_price": 149},
    {"title": "3 месяца", "days": 90, "stars_price": 349},
]


async def seed() -> None:
    async with async_session_maker() as session:
        existing_guides = await guides_repo.list_all(session)
        if not existing_guides:
            for item in _DEMO_GUIDES:
                path = SAMPLE_DIR / item["file"]
                if not path.exists():
                    continue
                await guides_repo.create(
                    session,
                    title=item["title"],
                    description=item["description"],
                    category=item["category"],
                    file_id=str(path),
                    is_premium=item["is_premium"],
                    is_local_file=True,
                )

        existing_plans = await plans_repo.list_all(session)
        if not existing_plans:
            for plan in _DEMO_PLANS:
                await plans_repo.create(
                    session, title=plan["title"], days=plan["days"], stars_price=plan["stars_price"]
                )

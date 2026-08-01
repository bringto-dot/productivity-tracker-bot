from aiogram import Router

from bot.handlers import checkin, guides, referral, settings, start, stats, subscription
from bot.handlers.admin import broadcast as admin_broadcast
from bot.handlers.admin import guides as admin_guides
from bot.handlers.admin import panel as admin_panel
from bot.handlers.admin import plans as admin_plans
from bot.handlers.admin import stats as admin_stats
from bot.handlers.admin import users as admin_users
from bot.middlewares.state_reset import StateResetMiddleware


def build_root_router() -> Router:
    root = Router(name="root")
    root.callback_query.middleware(StateResetMiddleware())

    root.include_router(start.router)
    root.include_router(checkin.router)
    root.include_router(stats.router)
    root.include_router(guides.router)
    root.include_router(referral.router)
    root.include_router(subscription.router)
    root.include_router(settings.router)

    root.include_router(admin_panel.router)
    root.include_router(admin_stats.router)
    root.include_router(admin_users.router)
    root.include_router(admin_guides.router)
    root.include_router(admin_plans.router)
    root.include_router(admin_broadcast.router)
    return root

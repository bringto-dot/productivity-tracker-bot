from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models import Guide, SubscriptionPlan, User
from bot.keyboards.common import pagination_row


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Аналитика", callback_data="admin:stats")
    builder.button(text="👥 Пользователи", callback_data="admin:users")
    builder.button(text="📚 Гайды", callback_data="admin:guides")
    builder.button(text="⭐ Тарифы", callback_data="admin:plans")
    builder.button(text="📣 Рассылка", callback_data="admin:broadcast")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:main"))
    return builder.as_markup()


def admin_back_keyboard(callback_data: str = "admin:menu") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data))
    return builder.as_markup()


def admin_guides_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📖 Гайды", callback_data="admin:g:list:guide:0"))
    builder.row(InlineKeyboardButton(text="🏋️ Тренировки", callback_data="admin:g:list:training:0"))
    builder.row(InlineKeyboardButton(text="🎓 Лекции", callback_data="admin:g:list:lecture:0"))
    builder.row(InlineKeyboardButton(text="➕ Добавить материал", callback_data="admin:g:add"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin:menu"))
    return builder.as_markup()


def admin_guides_list_keyboard(
    guides: list[Guide], category: str, page: int, total_pages: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for guide in guides:
        mark = "⭐ " if guide.is_premium else ""
        builder.row(InlineKeyboardButton(text=f"{mark}{guide.title}", callback_data=f"admin:g:view:{guide.id}"))
    pagination_row(builder, f"admin:g:list:{category}", page, total_pages)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin:guides"))
    return builder.as_markup()


def admin_guide_category_pick_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📖 Гайд", callback_data="admin:g:setcat:guide"))
    builder.row(InlineKeyboardButton(text="🏋️ Тренировка", callback_data="admin:g:setcat:training"))
    builder.row(InlineKeyboardButton(text="🎓 Лекция", callback_data="admin:g:setcat:lecture"))
    return builder.as_markup()


def admin_yes_no_keyboard(yes_cb: str, no_cb: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=yes_cb),
        InlineKeyboardButton(text="❌ Нет", callback_data=no_cb),
    )
    return builder.as_markup()


def admin_guide_view_keyboard(guide_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🗑 Удалить", callback_data=f"admin:g:del:{guide_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin:guides"))
    return builder.as_markup()


def admin_plans_keyboard(plans: list[SubscriptionPlan]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for plan in plans:
        status = "✅" if plan.is_active else "🚫"
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {plan.title} — {plan.days} дн. / {plan.stars_price}⭐",
                callback_data=f"admin:p:view:{plan.id}",
            )
        )
    builder.row(InlineKeyboardButton(text="➕ Новый тариф", callback_data="admin:p:add"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin:menu"))
    return builder.as_markup()


def admin_plan_view_keyboard(plan: SubscriptionPlan) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    toggle_text = "🚫 Деактивировать" if plan.is_active else "✅ Активировать"
    builder.row(InlineKeyboardButton(text=toggle_text, callback_data=f"admin:p:toggle:{plan.id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin:plans"))
    return builder.as_markup()


def admin_users_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔍 Найти пользователя", callback_data="admin:u:search"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin:menu"))
    return builder.as_markup()


def admin_user_view_keyboard(user: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🎁 Выдать 7 дней премиума", callback_data=f"admin:u:grant:{user.id}:7"))
    builder.row(InlineKeyboardButton(text="🎁 Выдать 30 дней премиума", callback_data=f"admin:u:grant:{user.id}:30"))
    ban_text = "✅ Разбанить" if user.is_banned else "🚫 Забанить"
    builder.row(InlineKeyboardButton(text=ban_text, callback_data=f"admin:u:ban_toggle:{user.id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin:users"))
    return builder.as_markup()


def admin_broadcast_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📣 Начать рассылку", callback_data="admin:b:start"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin:menu"))
    return builder.as_markup()


def admin_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Отправить всем", callback_data="admin:b:confirm"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="admin:b:cancel"),
    )
    return builder.as_markup()

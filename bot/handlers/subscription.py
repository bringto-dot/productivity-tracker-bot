from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.database.repo import analytics as analytics_repo
from bot.database.repo import payments as payments_repo
from bot.database.repo import plans as plans_repo
from bot.database.repo import users as users_repo
from bot.keyboards.subscription import plans_keyboard
from bot.services.i18n import t
from bot.services.stars_payments import CURRENCY, build_payload, build_prices, parse_payload

router = Router(name="subscription")


@router.callback_query(F.data == "menu:subscription")
async def cb_subscription_menu(callback: CallbackQuery, session: AsyncSession, user: User, lang: str) -> None:
    plans = await plans_repo.list_active(session)
    text = t("subscription.no_plans", lang) if not plans else t("subscription.title", lang)
    if user.has_active_premium:
        active_line = t("subscription.active_until", lang, date=user.premium_until.strftime("%Y-%m-%d %H:%M"))
        text = f"{active_line}\n\n{text}"

    await callback.message.edit_text(text, reply_markup=plans_keyboard(lang, plans))
    await callback.answer()


@router.callback_query(F.data.startswith("sub:plan:"))
async def cb_choose_plan(callback: CallbackQuery, session: AsyncSession, lang: str) -> None:
    plan_id = int(callback.data.split(":")[-1])
    plan = await plans_repo.get(session, plan_id)
    if plan is None or not plan.is_active:
        await callback.answer()
        return

    await callback.answer()
    await callback.message.answer_invoice(
        title=plan.title,
        description=t("subscription.invoice_description", lang, days=plan.days),
        payload=build_payload(plan.id),
        currency=CURRENCY,
        prices=build_prices(plan.stars_price),
    )


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery, session: AsyncSession) -> None:
    plan_id = parse_payload(pre_checkout_query.invoice_payload)
    plan = await plans_repo.get(session, plan_id) if plan_id is not None else None
    if plan is None or not plan.is_active:
        await pre_checkout_query.answer(ok=False, error_message="Этот тариф больше недоступен.")
        return
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message, session: AsyncSession, user: User, lang: str) -> None:
    payment_info = message.successful_payment
    plan_id = parse_payload(payment_info.invoice_payload)
    plan = await plans_repo.get(session, plan_id) if plan_id is not None else None

    if plan is not None:
        new_until = await users_repo.grant_premium_days(session, user, plan.days)
    else:
        new_until = user.premium_until

    await payments_repo.create(
        session,
        user.id,
        plan.id if plan else None,
        payment_info.telegram_payment_charge_id,
        payment_info.total_amount,
    )
    await analytics_repo.log_event(
        session, user.id, "subscribe", {"plan_id": plan_id, "stars": payment_info.total_amount}
    )

    await message.answer(t("subscription.success", lang, date=new_until.strftime("%Y-%m-%d %H:%M")))

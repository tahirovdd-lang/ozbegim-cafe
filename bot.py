import asyncio
import logging
import json
import os
import time

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo,
    InlineKeyboardMarkup, InlineKeyboardButton
)

logging.basicConfig(level=logging.INFO)

# ====== НАСТРОЙКИ ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден. Добавь переменную окружения BOT_TOKEN.")

# ✅ твои данные
BOT_USERNAME = "Uzbegim_kafe_bot"      # без @
ADMIN_ID = 6013591658                  # если админ другой — поменяй
CHANNEL_ID = "@Ozbegimsignature"       # канал

# ✅ WebApp (добавили v=1 чтобы Telegram не кешировал)
WEBAPP_URL = "https://tahirovdd-lang.github.io/ozbegim-cafe/?v=1"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ====== АНТИ-ДУБЛЬ START ======
_last_start: dict[int, float] = {}

def allow_start(user_id: int, ttl: float = 2.0) -> bool:
    now = time.time()
    prev = _last_start.get(user_id, 0.0)
    if now - prev < ttl:
        return False
    _last_start[user_id] = now
    return True


# ====== КНОПКИ ======
def kb_webapp_reply() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🍽 Открыть меню", web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True
    )

def kb_channel_button_to_bot() -> InlineKeyboardMarkup:
    """
    ✅ СИНЯЯ кнопка В ЗАКРЕПЕ КАНАЛА, которая ведёт В БОТА (не в WebApp).
    Это inline-кнопка с url на бота.
    """
    bot_link = f"https://t.me/{BOT_USERNAME}"
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔵 Перейти в бот", url=bot_link)]]
    )


# ====== ТЕКСТ ======
def welcome_text() -> str:
    return (
        "✨ <b>O'ZBEGIM Cafe</b>\n\n"
        "Нажмите кнопку ниже, чтобы открыть меню.\n"
        "✅ После заказа мы пришлём подтверждение сюда."
    )


# ====== /start ======
@dp.message(CommandStart())
async def start(message: types.Message):
    if not allow_start(message.from_user.id, ttl=2.0):
        return
    await message.answer(welcome_text(), reply_markup=kb_webapp_reply())


@dp.message(Command("startapp"))
async def startapp(message: types.Message):
    if not allow_start(message.from_user.id, ttl=2.0):
        return
    await message.answer(welcome_text(), reply_markup=kb_webapp_reply())


# ====== ПОСТ В КАНАЛ (с закрепом и синей кнопкой в бот) ======
@dp.message(Command("post_menu"))
async def post_menu(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔️ Нет доступа.")

    text = (
        "🍽 <b>O'ZBEGIM Cafe</b>\n\n"
        "Чтобы открыть меню и оформить заказ — перейдите в бот:\n"
        "👇 Нажмите синюю кнопку ниже"
    )

    try:
        sent = await bot.send_message(CHANNEL_ID, text, reply_markup=kb_channel_button_to_bot())

        # пробуем закрепить автоматически
        try:
            await bot.pin_chat_message(CHANNEL_ID, sent.message_id, disable_notification=True)
            await message.answer("✅ Пост отправлен в канал и закреплён.")
        except Exception:
            await message.answer(
                "✅ Пост отправлен в канал.\n"
                "⚠️ Не удалось закрепить — дай боту право «Закреплять сообщения» или закрепи вручную."
            )

    except Exception as e:
        logging.exception("CHANNEL POST ERROR")
        await message.answer(f"❌ Ошибка отправки в канал: <code>{e}</code>")


# ====== ВСПОМОГАТЕЛЬНЫЕ ======
def fmt_sum(n: int) -> str:
    try:
        n = int(n)
    except Exception:
        n = 0
    return f"{n:,}".replace(",", " ")


def tg_label(u: types.User) -> str:
    return f"@{u.username}" if u.username else u.full_name


def clean_str(v) -> str:
    return ("" if v is None else str(v)).strip()


# ====== ЗАКАЗ ИЗ WEBAPP ======
@dp.message(F.web_app_data)
async def webapp_data(message: types.Message):
    raw = message.web_app_data.data
    logging.info(f"WEBAPP DATA RAW: {raw}")

    await message.answer("✅ <b>Получил заказ.</b> Обрабатываю…")

    try:
        data = json.loads(raw) if raw else {}
    except Exception:
        data = {}

    order = data.get("order", {})
    if not isinstance(order, dict):
        order = {}

    total_num = int(data.get("total_num", 0) or 0)
    total_str = clean_str(data.get("total")) or fmt_sum(total_num)

    payment = clean_str(data.get("payment")) or "—"
    order_type = clean_str(data.get("type")) or "—"
    address = clean_str(data.get("address")) or "—"
    phone = clean_str(data.get("phone")) or "—"
    comment = clean_str(data.get("comment"))
    order_id = clean_str(data.get("order_id")) or "—"

    pay_label = {"cash": "💵 Наличные", "click": "💳 Безнал (CLICK)"}.get(payment, payment)
    type_label = {"delivery": "🚚 Доставка", "pickup": "🏃 Самовывоз"}.get(order_type, order_type)

    lines = []
    for item, qty in order.items():
        try:
            q = int(qty)
        except Exception:
            q = qty
        if isinstance(q, int) and q <= 0:
            continue
        lines.append(f"• {item} × {q}")
    if not lines:
        lines = ["⚠️ Корзина пустая"]

    # ====== АДМИН ======
    admin_text = (
        "🚨 <b>НОВЫЙ ЗАКАЗ O'ZBEGIM</b>\n"
        f"🆔 <b>{order_id}</b>\n\n"
        + "\n".join(lines) +
        f"\n\n💰 <b>Сумма:</b> {total_str} сум"
        f"\n🚚 <b>Тип:</b> {type_label}"
        f"\n💳 <b>Оплата:</b> {pay_label}"
        f"\n📍 <b>Адрес:</b> {address}"
        f"\n📞 <b>Телефон:</b> {phone}"
        f"\n👤 <b>Telegram:</b> {tg_label(message.from_user)}"
    )
    if comment:
        admin_text += f"\n💬 <b>Комментарий:</b> {comment}"

    await bot.send_message(ADMIN_ID, admin_text)

    # ====== КЛИЕНТ ======
    client_text = (
        "✅ <b>Ваш заказ принят!</b>\n"
        "🙏 Спасибо за заказ!\n\n"
        f"🆔 <b>{order_id}</b>\n\n"
        "<b>Состав заказа:</b>\n"
        + "\n".join(lines) +
        f"\n\n💰 <b>Сумма:</b> {total_str} сум"
        f"\n🚚 <b>Тип:</b> {type_label}"
        f"\n💳 <b>Оплата:</b> {pay_label}"
        f"\n📍 <b>Адрес:</b> {address}"
        f"\n📞 <b>Телефон:</b> {phone}"
    )
    if comment:
        client_text += f"\n💬 <b>Комментарий:</b> {comment}"

    await message.answer(client_text)


# ====== ЗАПУСК ======
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

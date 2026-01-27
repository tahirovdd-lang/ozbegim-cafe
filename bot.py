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

BOT_USERNAME = "kadima_cafe_bot"  # без @ (можешь сменить позже)
ADMIN_ID = 6013591658
CHANNEL_ID = "@Kadimasignaturetaste"

# ⚠️ ВАЖНО: версия, чтобы Telegram не кешировал старый сайт
WEBAPP_URL = "https://tahirovdd-lang.github.io/kadima-menu/?v=3"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ====== АНТИ-ДУБЛЬ START ======
_last_start: dict[int, float] = {}

def allow_start(user_id: int, ttl: float = 2.0) -> bool:
    """
    Telegram иногда вызывает /start два раза при очистке истории + заходе через канал.
    Эта защита пропускает только первый вызов в течение ttl секунд.
    """
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


def kb_channel_deeplink() -> InlineKeyboardMarkup:
    deeplink = f"https://t.me/{BOT_USERNAME}?startapp=menu"
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🍽 Открыть меню", url=deeplink)]]
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


# ====== ПОСТ В КАНАЛ ======
@dp.message(Command("post_menu"))
async def post_menu(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔️ Нет доступа.")

    text = "🍽 <b>O'ZBEGIM Cafe</b>\nНажмите кнопку ниже, чтобы открыть меню:"
    try:
        sent = await bot.send_message(CHANNEL_ID, text, reply_markup=kb_channel_deeplink())
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
    tr

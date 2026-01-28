import os
import json
import logging
import asyncio

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo,
    InlineKeyboardMarkup, InlineKeyboardButton
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден в переменных окружения")

# ====== НАСТРОЙКИ ======
BOT_USERNAME = "Uzbegim_kafe_bot"          # без @
ADMIN_ID = 6013591658                     # твой id
CHANNEL_ID = "@Ozbegimsignature"          # канал (может не использоваться в этом файле)
WEBAPP_URL = "https://tahirovdd-lang.github.io/ozbegim-cafe/?v=1"  # WebApp

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

WELCOME_3LANG = (
    "🇷🇺 <b>Добро пожаловать в O'ZBEGIM!</b>\n"
    "Нажмите кнопку <b>🍽 Меню</b> ниже.\n\n"
    "🇺🇿 <b>O'ZBEGIM ga xush kelibsiz!</b>\n"
    "<b>🍽 Menyu</b> tugmasini bosing.\n\n"
    "🇬🇧 <b>Welcome to O'ZBEGIM!</b>\n"
    "Tap <b>🍽 Menu</b> below."
)

def menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🍽 Меню", web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True
    )

def channel_button_kb() -> InlineKeyboardMarkup:
    # Эта inline-кнопка — если ты захочешь прикреплять в пост/закреп в канале
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍽 Открыть меню", url=WEBAPP_URL)]
        # или если нужно вести в бота:
        # [InlineKeyboardButton(text="🍽 Открыть меню", url=f"https://t.me/{BOT_USERNAME}?start=menu")]
    ])

# ========= START / MENU =========
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(WELCOME_3LANG, reply_markup=menu_kb())

@dp.message(Command("menu"))
async def menu_cmd(message: types.Message):
    await message.answer(WELCOME_3LANG, reply_markup=menu_kb())

# ========= ПРИЁМ ДАННЫХ ИЗ WEBAPP =========
@dp.message(F.web_app_data)
async def webapp_order(message: types.Message):
    """
    Ожидаем JSON из Telegram WebApp:
    Telegram.WebApp.sendData(JSON.stringify({...}))
    """
    raw = message.web_app_data.data

    try:
        data = json.loads(raw)
    except Exception:
        data = {"raw": raw}

    # Красивый текст админу
    pretty = json.dumps(data, ensure_ascii=False, indent=2)

    await message.answer("✅ Заказ получен! Спасибо 😊")

    # Отправим админу
    try:
        await bot.send_message(
            ADMIN_ID,
            "🧾 <b>Новый заказ из WebApp</b>\n"
            f"👤 От: {message.from_user.full_name} (id: <code>{message.from_user.id}</code>)\n\n"
            f"<pre>{pretty}</pre>"
        )
    except Exception as e:
        logging.exception("Не удалось отправить заказ админу: %s", e)

# ========= (необязательно) TEST =========
@dp.message(Command("ping"))
async def ping(message: types.Message):
    await message.answer("pong ✅")

async def main():
    logging.info("🚀 Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

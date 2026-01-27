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
CHANNEL_ID = "@Ozbegimsignature"          # канал
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
    # Кнопка, которая будет видна справа от закрепа (как у Kadima)
    # Вариант 1 (прямо открыть сайт): WEBAPP_URL
    # Вариант 2 (открыть бота): deep-link на бота -> покажет кнопку меню
    # Если хочешь как у Kadima (кнопка сверху в канале) — чаще всего достаточно WEBAPP_URL.
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍽 Открыть меню", url=WEBAPP_URL)]
        # если надо именно в бота:
        # [InlineKeyboardButton(text="🍽 Открыть меню", url=f"https://t.me/{BOT_USERNAME}?start=menu")]
    ])

# ========= START / MENU =========
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(WELCOME_3LANG, reply_markup=menu_kb())

@dp.message(Command("menu"))
async def menu_cmd(message: types.Message):
    await message.answer(WELCOME_3LANG, reply_markup=menu_kb())

# ========= ПРИЁМ ЗАКАЗОВ ИЗ WEBAPP =========
@dp.message(F.web_app_data)
async def webapp_orde_



import os
import json
import logging
import asyncio

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.filters.command import CommandObject
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден в переменных окружения")

# ====== НАСТРОЙКИ ======
BOT_USERNAME = "Uzbegim_kafe_bot"          # без @
ADMIN_ID = 6013591658                     # твой id
CHANNEL_ID = "@Ozbegimsignature"          # канал (здесь не используется, оставил для твоих будущих задач)
WEBAPP_URL = "https://tahirovdd-lang.github.io/ozbegim-cafe/?v=1"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ====== ТЕКСТЫ 3 ЯЗЫКА (как было) ======
WELCOME_3LANG = (
    "🇷🇺 <b>Добро пожаловать в O'ZBEGIM!</b>\n"
    "Нажмите кнопку <b>🍽 Меню</b> ниже.\n\n"
    "🇺🇿 <b>O'ZBEGIM ga xush kelibsiz!</b>\n"
    "<b>🍽 Menyu</b> tugmasini bosing.\n\n"
    "🇬🇧 <b>Welcome to O'ZBEGIM!</b>\n"
    "Tap <b>🍽 Menu</b> below."
)

# Кнопка меню (внизу) с текстом на 3 языках
MENU_BTN_TEXT_3LANG = "🍽 Меню / 🍽 Menyu / 🍽 Menu"

def menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=MENU_BTN_TEXT_3LANG, web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True
    )

async def send_welcome(message: types.Message):
    await message.answer(WELCOME_3LANG, reply_markup=menu_kb())

# ========= START =========
@dp.message(CommandStart())
async def start(message: types.Message, command: CommandObject):
    # Если человек пришёл из канала по ссылке вида:
    # https://t.me/Uzbegim_kafe_bot?start=menu
    # тогда command.args == "menu"
    await send_welcome(message)

# ========= /menu =========
@dp.message(Command("menu"))
async def menu_cmd(message: types.Message):
    await send_welcome(message)

# ========= Нажатие на кнопку меню (текст) =========
@dp.message(F.text == MENU_BTN_TEXT_3LANG)
async def menu_button(message: types.Message):
    # Не обязательно что-то отвечать — WebApp откроется автоматически,
    # но можно оставить подсказку/тишину. Я оставлю тишину.
    pass

# ========= ПРИЁМ ДАННЫХ ИЗ WEBAPP =========
@dp.message(F.web_app_data)
async def webapp_order(message: types.Message):
    raw = message.web_app_data.data

    try:
        data = json.loads(raw)
    except Exception:
        data = {"raw": raw}

    pretty = json.dumps(data, ensure_ascii=False, indent=2)

    await message.answer("✅ Заказ получен! Спасибо 😊", reply_markup=menu_kb())

    try:
        await bot.send_message(
            ADMIN_ID,
            "🧾 <b>Новый заказ из WebApp</b>\n"
            f"👤 От: {message.from_user.full_name} (id: <code>{message.from_user.id}</code>)\n\n"
            f"<pre>{pretty}</pre>"
        )
    except Exception as e:
        logging.exception("Не удалось отправить заказ админу: %s", e)

# ========= fallback: если человек написал что-то без /start =========
@dp.message()
async def fallback(message: types.Message):
    # Чтобы не было ситуации “перешёл в бот, дальше ничего не происходит”,
    # если человек напишет любое сообщение — покажем меню.
    await send_welcome(message)

async def main():
    logging.info("🚀 Bot started (polling)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

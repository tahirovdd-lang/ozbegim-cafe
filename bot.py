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
ADMIN_ID = 6013591658
WEBAPP_URL = "https://tahirovdd-lang.github.io/ozbegim-cafe/?v=1"

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

# ====== ПРИВЕТСТВИЕ (3 ЯЗЫКА + ФЛАГИ) ======
WELCOME_3LANG = (
    "🇷🇺 <b>Добро пожаловать в O'ZBEGIM!</b> 👋\n"
    "Выберите любимые блюда и оформите заказ — просто нажмите «Открыть» ниже.\n\n"
    "🇺🇿 <b>O'ZBEGIM ga xush kelibsiz!</b> 👋\n"
    "Sevimli taomlaringizni tanlang va buyurtma bering — "
    "buning uchun pastdagi «Ochish» tugmasini bosing.\n\n"
    "🇬🇧 <b>Welcome to O'ZBEGIM!</b> 👋\n"
    "Choose your favorite dishes and place an order — just tap “Open” below."
)

# ====== КНОПКА МЕНЮ (НИЖНЯЯ) ======
MENU_BTN_TEXT = "Ochish / Открыть / Open"

def menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text=MENU_BTN_TEXT,
                web_app=WebAppInfo(url=WEBAPP_URL)
            )]
        ],
        resize_keyboard=True
    )

async def send_welcome(message: types.Message):
    await message.answer(WELCOME_3LANG, reply_markup=menu_kb())

# ========= START =========
@dp.message(CommandStart())
async def start(message: types.Message, command: CommandObject):
    await send_welcome(message)

# ========= /menu =========
@dp.message(Command("menu"))
async def menu_cmd(message: types.Message):
    await send_welcome(message)

# ========= НАЖАТИЕ КНОПКИ (ТЕКСТ) =========
@dp.message(F.text == MENU_BTN_TEXT)
async def menu_button(message: types.Message):
    # WebApp откроется автоматически
    pass

# ========= ПРИЁМ ДАННЫХ ИЗ WEBAPP =========
@dp.message(F.web_app_data)
async def webapp_order(message: types.Message):
    raw = message.web_app_data.data

    try:
        data = json.loads(raw)
    except Exception:
        data = {}

    # Ответ пользователю
    await message.answer(
        "✅ Заказ принят! Спасибо за ваш выбор 😊",
        reply_markup=menu_kb()
    )

    # Красивое сообщение админу (НЕ код, НЕ <pre>)
    order = data.get("order", {})
    items = "\n".join(
        [f"• {name} × {qty}" for name, qty in order.items()]
    ) if order else "• —"

    text_admin = (
        "📩 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"👤 Клиент: {message.from_user.full_name}\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"📞 Телефон: <b>{data.get('phone','—')}</b>\n"
        f"🚚 Тип: <b>{data.get('type','—')}</b>\n"
        f"📍 Адрес: <b>{data.get('address','—')}</b>\n"
        f"💳 Оплата: <b>{data.get('payment','—')}</b>\n\n"
        f"{items}\n\n"
        f"💰 <b>{data.get('total','—')}</b> сум"
    )

    await bot.send_message(ADMIN_ID, text_admin)

# ========= FALLBACK =========
@dp.message()
async def fallback(message: types.Message):
    # Если пользователь написал что-то без /start
    await send_welcome(message)

async def main():
    logging.info("🚀 Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

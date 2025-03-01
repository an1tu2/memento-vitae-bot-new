import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

# 🔹 Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env!")
if not WEBHOOK_URL:
    raise ValueError("❌ WEBHOOK_URL не найден в .env!")

# 🔹 Инициализация бота
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# 🔹 Создаём клавиатуру
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Старт"), KeyboardButton(text="📖 Инфо")],
        [KeyboardButton(text="🔄 Обновить статус")]
    ],
    resize_keyboard=True
)

# 🔹 Обработчик команды /start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот, работающий через Vercel.\n\nВыбери команду:",
        reply_markup=main_keyboard
    )

# 🔹 Обработчик текстовых кнопок
@dp.message(lambda message: message.text in ["🚀 Старт", "📖 Инфо", "🔄 Обновить статус"])
async def button_handler(message: types.Message):
    if message.text == "🚀 Старт":
        await message.answer("🚀 Ты запустил бота! Введи /help для списка команд.")
    elif message.text == "📖 Инфо":
        await message.answer("ℹ️ Этот бот развёрнут на Vercel и всегда доступен!")
    elif message.text == "🔄 Обновить статус":
        await message.answer("🔄 Бот работает и отвечает мгновенно!")

# 🔹 Создаём приложение aiohttp
app = web.Application()

# 🔹 Маршрут для вебхука
async def root_handler(request: web.Request):
    if request.method == "GET":
        return web.Response(text="✅ Бот активен и работает!")
    return await webhook_handler.handle(request)

# 🔹 Настройка webhook
webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
app.router.add_route("*", "/", root_handler)
setup_application(app, dp, bot=bot)

async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)

app.on_startup.append(on_startup)

# 🔹 Экспорт приложения для Vercel
handler = app

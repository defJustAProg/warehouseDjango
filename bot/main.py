from fastapi import FastAPI
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from datetime import date
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import uvicorn

app = FastAPI()
load_dotenv()

# Формат тела запроса для отправки данных о добавленном товаре пользователю телеграм 
class Message(BaseModel):
    id: str = Field(None)
    length: int = Field(...)
    weight: int = Field(...)
    put_date: date = Field(None)
    delete_date: date = Field(None)

# Множество идентификаторов пользователей для рассылки, запустивших бота
user_ids = set()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ['BOT_TOKEN'])
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_ids.add(message.from_user.id)
    await message.reply("Hello!")

# Отправка информации о добавленном товаре пользователям
@app.post("/sendMessage")
async def send_message(record: Message):
    for user_id in user_ids:
        try:
            await bot.send_message(
                user_id,
                f"<b>Добавлен новый товар:</b>\
                <b>ID: {record.id}</b>\
                <b>Длина: {record.length}</b>\
                <b>Вес: {record.weight}</b>\
                <b>Дата добавления: {record.put_date}</b>\
                <b>Дата удаления: {record.delete_date}</b>",
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

async def start_polling():
    await dp.start_polling(bot)

async def main():
    task = asyncio.create_task(start_polling())
    config = uvicorn.Config(app, host=os.getenv('BOT_HOST', '127.0.0.1'), port=int(os.getenv('BOT_PORT', 8001)))
    server = uvicorn.Server(config)
    await asyncio.gather(server.serve(), task)

if __name__ == "__main__":
    asyncio.run(main())
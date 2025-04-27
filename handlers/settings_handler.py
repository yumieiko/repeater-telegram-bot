import collections
from typing import Collection
from aiogram import Dispatcher, F, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi


class ChatID(StatesGroup):
    forward_chat_id = State()

def initialize(dp: Dispatcher, bot: Bot):
    @dp.callback_query(lambda F: F.data == "set_forward_chat_id")
    async def set_forward_chat_id(callback: CallbackQuery, state: FSMContext):
        await bot.send_message(callback.from_user.id, "Напиши ID Чата в который будут пересылаться сообщения")
        await state.set_state(ChatID.forward_chat_id)


    # Saving ChatID to database
    @dp.message(ChatID.forward_chat_id)
    async def save_forward_chat_id(message: Message, state: FSMContext):
        client = AsyncIOMotorClient("mongodb://localhost:27017", server_api=ServerApi('1'))        
        collection = client["reporter"]["chatid"]
        await state.update_data(name=message.text)

        await collection.delete_many({})
        await collection.insert_one({"chatid": message.text})

        await bot.send_message(message.from_user.id, "Ваш айди чата сохранен!")
        client.close()

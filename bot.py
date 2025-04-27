import asyncio
import collections
import logging
import sys

from aiogram import Bot, Dispatcher, client
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, Message, message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from motor.motor_asyncio import AsyncIOMotorClient
import handlers.settings_handler
import config
from aiogram.fsm.context import FSMContext
dp = Dispatcher()
bot = Bot(token=config.get_token(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@dp.message(CommandStart())
async def starter(message: Message):
    await message.answer("Привет!\nты можешь отправить сюда свое сообщение и мы рассмотрим его!")
    
@dp.message(Command("settings"))
async def settings(message: Message):
   
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(InlineKeyboardButton(text="Задать Chat ID", callback_data="set_forward_chat_id"))
    
    if config.get_adminid() == message.from_user.id:
        await message.answer(
            "Настройки.",
            reply_markup=keyboard_builder.as_markup()
        )
    else:
        await message.answer(
            "Ты не админ!"
        )


@dp.message()
async def forwardmessage(message: Message, state: FSMContext):
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    collection = client['reporter']['chatid']
    
    current_state = await state.get_state()
    if not current_state is None:
        await state.update_data(name=message.text)
        await collection.delete_many({})
        await collection.insert_one({"chatid": message.text})
        await bot.send_message(message.from_user.id, "Ваш айди чата сохранен!")
        client.close()
        await state.clear()
    
    
    query = {"chatid": {"$exists": True}}
    result = await collection.find_one(query)

    if result and "chatid" in result:
        await message.forward(int(result['chatid']))
    else:
        print("No document with chat_id found.")

async def main() -> None:
    handlers.settings_handler.initialize(dp, bot)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

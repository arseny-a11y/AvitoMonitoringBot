from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

base_router = Router()

@base_router.message(CommandStart())
async def start_command(message: Message):
    await message.answer("Привет!")
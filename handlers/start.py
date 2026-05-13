from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards import main_menu_kb

router = Router()

WELCOME = (
    "📜 <b>Лексикон XVIII века</b>\n\n"
    "Добро пожаловать! Здесь собраны устаревшие и заимствованные слова "
    "русского языка XVIII века — каждое со значением, цитатой из источника "
    "и связью с реформой эпохи.\n\n"
    "Выберите раздел в меню ниже."
)

MENU_TEXT = "Выберите раздел:"


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME, reply_markup=main_menu_kb())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(MENU_TEXT, reply_markup=main_menu_kb())


@router.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(MENU_TEXT, reply_markup=main_menu_kb())
    await callback.answer()

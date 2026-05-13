import logging
import os

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, ErrorEvent, Message

from config import ABOUT_ERA_PATH
from keyboards import era_nav_kb, main_menu_kb

router = Router()
logger = logging.getLogger(__name__)


ABOUT_TEXT = (
    "<b>Проект «Лексикон XVIII века»</b>\n\n"
    "Интерактивный словарь устаревших и заимствованных слов русского языка XVIII века.\n\n"
    "<b>Авторы:</b>\n"
    "Ляхов Дмитрий, Ширяев Иван, Острейкова София, Карпухин Симеон, Минич Марк\n\n"
    "<b>Курс:</b> История России, ФКН ВШЭ, ПАД, 2026 г.\n\n"
    "<b>Источники цитат:</b>\n"
    "• Письма и бумаги Петра Великого\n"
    "• Указы Петра I и Екатерины II\n"
    "• Сочинения Д.И. Фонвизина, М.В. Ломоносова, Г.Р. Державина, А.Н. Радищева\n"
    "• Записки Екатерины II\n"
    "• Мемуары А.Т. Болотова\n\n"
    "<b>Словари:</b>\n"
    "• Словарь русского языка XVIII века (под ред. Ю.С. Сорокина)\n"
    "• Словарь Академии Российской 1789–1794 гг.\n\n"
    "<b>Научная литература:</b>\n"
    "• Виноградов В.В. Очерки по истории русского литературного языка XVII–XIX вв.\n"
    "• Успенский Б.А. Краткий очерк истории русского литературного языка.\n"
    "• Биржакова Е.Э., Войнова Л.А., Кутина Л.Л. Очерки по исторической лексикологии русского языка XVIII века.\n"
    "• Лотман Ю.М. Беседы о русской культуре.\n"
    "• Живов В.М. Язык и культура в России XVIII века."
)

ERA_UNAVAILABLE = "Раздел временно недоступен."


def _load_era_pages() -> list[str] | None:
    if not os.path.exists(ABOUT_ERA_PATH):
        return None
    try:
        with open(ABOUT_ERA_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return None
    pages = [p.strip() for p in content.split("\n---\n") if p.strip()]
    return pages or None


async def _show_era_page(message_or_cb, page: int, is_callback: bool) -> None:
    pages = _load_era_pages()
    if not pages:
        if is_callback:
            await message_or_cb.message.edit_text(ERA_UNAVAILABLE, reply_markup=main_menu_kb())
            await message_or_cb.answer()
        else:
            await message_or_cb.answer(ERA_UNAVAILABLE, reply_markup=main_menu_kb())
        return
    page = max(0, min(page, len(pages) - 1))
    text = pages[page]
    kb = era_nav_kb(page, len(pages))
    if is_callback:
        await message_or_cb.message.edit_text(text, reply_markup=kb)
        await message_or_cb.answer()
    else:
        await message_or_cb.answer(text, reply_markup=kb)


@router.message(Command("era"))
async def cmd_era(message: Message) -> None:
    await _show_era_page(message, 0, is_callback=False)


@router.callback_query(F.data.startswith("era_page_"))
async def cb_era_page(callback: CallbackQuery) -> None:
    try:
        page = int(callback.data[len("era_page_"):])
    except ValueError:
        await callback.answer()
        return
    await _show_era_page(callback, page, is_callback=True)


@router.callback_query(F.data == "era_noop")
async def cb_era_noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.message(Command("about"))
async def cmd_about(message: Message) -> None:
    await message.answer(ABOUT_TEXT, reply_markup=main_menu_kb())


@router.callback_query(F.data == "about")
async def cb_about(callback: CallbackQuery) -> None:
    await callback.message.edit_text(ABOUT_TEXT, reply_markup=main_menu_kb())
    await callback.answer()


@router.message()
async def fallback_message(message: Message) -> None:
    await message.answer("Используйте меню или команды. /help — справка.")


@router.errors()
async def errors_handler(event: ErrorEvent) -> bool:
    logger.exception("Unhandled error: %s", event.exception)
    update = event.update
    try:
        if update.message:
            await update.message.answer("Произошла ошибка. /start — начать заново.")
        elif update.callback_query:
            await update.callback_query.answer(
                "Произошла ошибка. /start — начать заново.", show_alert=True,
            )
    except Exception:
        logger.exception("Failed to notify user about error")
    return True

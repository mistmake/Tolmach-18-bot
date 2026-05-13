from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from core.storage import (
    CATEGORIES,
    WORDS_BY_ID,
    pick_random_unseen_word,
    words_in_category,
)
from keyboards import (
    categories_kb,
    category_words_kb,
    word_card_kb,
    word_detail_kb,
)

router = Router()


def render_card(word: dict) -> str:
    return (
        f"📜 <b>{word['word']}</b> ({word['stress']})\n\n"
        f"📖 <b>Значение в XVIII в.:</b>\n{word['meaning']}\n\n"
        f"🌍 <b>Происхождение:</b>\n{word['origin']}\n\n"
        f"💬 <b>Из источника:</b>\n<i>«{word['quote']}»</i>\n— {word['source']}\n\n"
        f"⚙️ <b>Связь с реформой:</b>\n{word['reform_link']}\n\n"
        f"⏳ <b>Судьба слова сегодня:</b>\n{word['today']}"
    )


def render_category_list(category: str) -> str:
    title = CATEGORIES[category]
    words = words_in_category(category)
    lines = [f"{title}\n"]
    for i, w in enumerate(words, 1):
        lines.append(f"{i}. {w['word']}")
    lines.append("\nНажмите номер для подробностей.")
    return "\n".join(lines)


@router.message(Command("word"))
async def cmd_word(message: Message) -> None:
    word = pick_random_unseen_word(message.from_user.id)
    await message.answer(render_card(word), reply_markup=word_card_kb())


@router.callback_query(F.data == "word_random")
async def cb_word_random(callback: CallbackQuery) -> None:
    word = pick_random_unseen_word(callback.from_user.id)
    await callback.message.edit_text(render_card(word), reply_markup=word_card_kb())
    await callback.answer()


@router.message(Command("categories"))
async def cmd_categories(message: Message) -> None:
    await message.answer("Выберите категорию:", reply_markup=categories_kb())


@router.callback_query(F.data == "categories")
async def cb_categories(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Выберите категорию:", reply_markup=categories_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("cat_"))
async def cb_category(callback: CallbackQuery) -> None:
    category = callback.data[len("cat_"):]
    if category not in CATEGORIES:
        await callback.answer("Неизвестная категория", show_alert=True)
        return
    words = words_in_category(category)
    await callback.message.edit_text(
        render_category_list(category),
        reply_markup=category_words_kb(category, words),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_cat_"))
async def cb_back_to_cat(callback: CallbackQuery) -> None:
    category = callback.data[len("back_to_cat_"):]
    if category not in CATEGORIES:
        await callback.answer("Неизвестная категория", show_alert=True)
        return
    words = words_in_category(category)
    await callback.message.edit_text(
        render_category_list(category),
        reply_markup=category_words_kb(category, words),
    )
    await callback.answer()


@router.callback_query(F.data.regexp(r"^word_\d+$"))
async def cb_word_by_id(callback: CallbackQuery) -> None:
    word_id = int(callback.data[len("word_"):])
    word = WORDS_BY_ID.get(word_id)
    if not word:
        await callback.answer("Слово не найдено", show_alert=True)
        return
    await callback.message.edit_text(
        render_card(word),
        reply_markup=word_detail_kb(word["category"]),
    )
    await callback.answer()

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.storage import CATEGORIES


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎲 Слово дня", callback_data="word_random"),
            InlineKeyboardButton(text="📖 Категории", callback_data="categories"),
        ],
        [
            InlineKeyboardButton(text="🎯 Квиз", callback_data="quiz"),
            InlineKeyboardButton(text="📚 Об эпохе", callback_data="era_page_0"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Об авторах", callback_data="about"),
        ],
    ])


def word_card_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎲 Ещё одно", callback_data="word_random"),
            InlineKeyboardButton(text="🏠 В меню", callback_data="menu"),
        ],
    ])


def categories_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=title, callback_data=f"cat_{key}")]
        for key, title in CATEGORIES.items()
    ]
    rows.append([InlineKeyboardButton(text="🏠 В меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def category_words_kb(category: str, words: list[dict]) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=str(i + 1), callback_data=f"word_{w['id']}")
        for i, w in enumerate(words)
    ]
    rows = []
    # две строки по 5 (если слов <= 10); для большего числа — добиваем по 5
    for i in range(0, len(buttons), 5):
        rows.append(buttons[i:i + 5])
    rows.append([
        InlineKeyboardButton(text="⬅️ К категориям", callback_data="categories"),
        InlineKeyboardButton(text="🏠 В меню", callback_data="menu"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def word_detail_kb(category: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ К списку", callback_data=f"back_to_cat_{category}"),
            InlineKeyboardButton(text="🏠 В меню", callback_data="menu"),
        ],
    ])


def quiz_modes_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔤 Угадай значение", callback_data="quiz_meaning")],
        [InlineKeyboardButton(text="💬 Угадай слово по цитате", callback_data="quiz_quote")],
        [InlineKeyboardButton(text="⏳ Сохранилось или устарело?", callback_data="quiz_today")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="menu")],
    ])


def quiz_options_kb(count: int) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=str(i + 1), callback_data=f"ans_{i}")
        for i in range(count)
    ]
    if count == 4:
        rows = [buttons[0:2], buttons[2:4]]
    else:
        rows = [buttons]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def quiz_after_answer_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="▶️ Следующий вопрос", callback_data="quiz_next"),
            InlineKeyboardButton(text="🛑 Завершить", callback_data="quiz_finish"),
        ],
    ])


def era_nav_kb(page: int, total: int) -> InlineKeyboardMarkup:
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"era_page_{page - 1}"))
    nav_row.append(InlineKeyboardButton(text=f"Стр. {page + 1} из {total}", callback_data="era_noop"))
    if page < total - 1:
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"era_page_{page + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=[
        nav_row,
        [InlineKeyboardButton(text="🏠 В меню", callback_data="menu")],
    ])

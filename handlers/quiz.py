from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from core.quiz_logic import build_question
from core.storage import WORDS_BY_ID, get_state, record_answer, reset_quiz
from keyboards import (
    main_menu_kb,
    quiz_after_answer_kb,
    quiz_modes_kb,
    quiz_options_kb,
)

router = Router()

NUMBER_EMOJI = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

MODE_TITLES = {
    "meaning": "🔤 <b>Вопрос {n}</b>\n\nЧто означало слово <b>«{word}»</b> в XVIII веке?",
    "quote": (
        "💬 <b>Вопрос {n}</b>\n\n"
        "Прочитайте цитату из источника XVIII века:\n\n"
        "<i>«{quote}»</i>\n— {source}\n\n"
        "Какое слово было пропущено?"
    ),
    "today": (
        "⏳ <b>Вопрос {n}</b>\n\n"
        "Слово <b>«{word}»</b> означало в XVIII в.:\n"
        "<i>{meaning}</i>\n\n"
        "Сохранилось ли оно в современном русском с тем же значением?"
    ),
}


def _format_options(options: list[str]) -> str:
    return "\n".join(f"{NUMBER_EMOJI[i]} {opt}" for i, opt in enumerate(options))


def _render_question(q: dict, question_number: int) -> str:
    if q["mode"] == "meaning":
        head = MODE_TITLES["meaning"].format(n=question_number, word=q["prompt_word"])
    elif q["mode"] == "quote":
        head = MODE_TITLES["quote"].format(
            n=question_number, quote=q["quote_with_blank"], source=q["source"],
        )
    elif q["mode"] == "today":
        head = MODE_TITLES["today"].format(
            n=question_number, word=q["prompt_word"], meaning=q["prompt_meaning"],
        )
    else:
        return ""
    return f"{head}\n\n{_format_options(q['options_full'])}"


def _verdict(percent: float) -> str:
    if percent >= 90:
        return "🏆 Превосходно! Вы знаете эпоху на уровне историка."
    if percent >= 70:
        return "👍 Хороший результат. Эпоха вам знакома."
    if percent >= 50:
        return "📚 Есть пробелы. Загляните в /categories."
    return "🤔 Эпоха ещё ждёт вашего изучения. Начните с /era."


async def _send_question(callback: CallbackQuery, user_id: int, mode: str) -> None:
    q = build_question(mode)
    if q is None:
        await callback.message.edit_text(
            "Не удалось сгенерировать вопрос. Попробуйте другой режим.",
            reply_markup=quiz_modes_kb(),
        )
        await callback.answer()
        return
    state = get_state(user_id)
    state["quiz_mode"] = mode
    state["current_question"] = q
    question_number = state["total"] + 1
    await callback.message.edit_text(
        _render_question(q, question_number),
        reply_markup=quiz_options_kb(len(q["options_full"])),
    )
    await callback.answer()


@router.message(Command("quiz"))
async def cmd_quiz(message: Message) -> None:
    reset_quiz(message.from_user.id)
    await message.answer("Выберите режим квиза:", reply_markup=quiz_modes_kb())


@router.callback_query(F.data == "quiz")
async def cb_quiz(callback: CallbackQuery) -> None:
    reset_quiz(callback.from_user.id)
    await callback.message.edit_text("Выберите режим квиза:", reply_markup=quiz_modes_kb())
    await callback.answer()


@router.callback_query(F.data.in_({"quiz_meaning", "quiz_quote", "quiz_today"}))
async def cb_quiz_mode(callback: CallbackQuery) -> None:
    mode = callback.data[len("quiz_"):]
    user_id = callback.from_user.id
    reset_quiz(user_id)
    await _send_question(callback, user_id, mode)


@router.callback_query(F.data.startswith("ans_"))
async def cb_answer(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    state = get_state(user_id)
    q = state.get("current_question")
    if not q:
        await callback.message.edit_text(
            "Сессия устарела, начните заново через /start",
        )
        await callback.answer()
        return
    try:
        chosen = int(callback.data[len("ans_"):])
    except ValueError:
        await callback.answer()
        return

    is_correct = chosen == q["correct_idx"]
    record_answer(user_id, is_correct)
    state["current_question"] = None
    state_after = get_state(user_id)
    correct_full = q["options_full"][q["correct_idx"]]
    word = WORDS_BY_ID.get(q["word_id"], {})

    if q["mode"] == "meaning":
        explanation = (
            f"<b>«{word.get('word', '')}»</b> — {correct_full}"
        )
    elif q["mode"] == "quote":
        explanation = (
            f"<b>«{correct_full}»</b> — {word.get('meaning', '')}"
        )
    else:
        explanation = (
            f"Судьба слова сегодня: {word.get('today', '')}"
        )

    if is_correct:
        text = (
            "✅ <b>Верно!</b>\n\n"
            f"{explanation}\n\n"
            f"📊 Счёт: {state_after['correct']}/{state_after['total']}"
        )
    else:
        text = (
            "❌ <b>Неверно.</b>\n\n"
            f"Правильный ответ: <b>{correct_full}</b>\n\n"
            f"{explanation}\n\n"
            f"📊 Счёт: {state_after['correct']}/{state_after['total']}"
        )

    await callback.message.edit_text(text, reply_markup=quiz_after_answer_kb())
    await callback.answer()


@router.callback_query(F.data == "quiz_next")
async def cb_quiz_next(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    state = get_state(user_id)
    mode = state.get("quiz_mode")
    if not mode:
        await callback.message.edit_text(
            "Сессия устарела, начните заново через /start",
        )
        await callback.answer()
        return
    await _send_question(callback, user_id, mode)


@router.callback_query(F.data == "quiz_finish")
async def cb_quiz_finish(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    state = get_state(user_id)
    total = state["total"]
    correct = state["correct"]
    percent = round((correct / total) * 100) if total else 0
    text = (
        "🏁 <b>Квиз завершён</b>\n\n"
        f"Правильных: {correct} из {total}\n"
        f"Точность: {percent}%\n\n"
        f"{_verdict(percent)}"
    )
    reset_quiz(user_id)
    await callback.message.edit_text(text, reply_markup=main_menu_kb())
    await callback.answer()


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    state = get_state(message.from_user.id)
    total = state["total"]
    correct = state["correct"]
    if total == 0:
        await message.answer("Вы ещё не играли в квиз. Начать: /quiz")
        return
    percent = round((correct / total) * 100)
    await message.answer(
        "📊 <b>Ваша статистика</b>\n\n"
        f"Всего вопросов: {total}\n"
        f"Правильных: {correct}\n"
        f"Точность: {percent}%"
    )

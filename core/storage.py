import json
import random

from config import WORDS_PATH


def _load_words() -> list[dict]:
    with open(WORDS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not data:
        raise RuntimeError(f"{WORDS_PATH}: ожидался непустой список словарных карточек")
    return data


WORDS: list[dict] = _load_words()
WORDS_BY_ID: dict[int, dict] = {w["id"]: w for w in WORDS}

CATEGORIES: dict[str, str] = {
    "state_society": "🏛 Государство и общество",
    "military": "⚔️ Военное и морское дело",
    "social_life": "🎭 Светская жизнь и этикет",
    "culture": "📚 Наука, искусство, литература",
}


def words_in_category(category: str) -> list[dict]:
    return [w for w in WORDS if w["category"] == category]


# user_id -> dict
user_state: dict[int, dict] = {}


def _empty_state() -> dict:
    return {
        "quiz_mode": None,
        "correct": 0,
        "total": 0,
        "current_question": None,
        "seen_random_word_ids": set(),
    }


def get_state(user_id: int) -> dict:
    if user_id not in user_state:
        user_state[user_id] = _empty_state()
    return user_state[user_id]


def reset_quiz(user_id: int) -> None:
    state = get_state(user_id)
    state["quiz_mode"] = None
    state["correct"] = 0
    state["total"] = 0
    state["current_question"] = None


def record_answer(user_id: int, is_correct: bool) -> None:
    state = get_state(user_id)
    state["total"] += 1
    if is_correct:
        state["correct"] += 1


def reset_seen_words(user_id: int) -> None:
    get_state(user_id)["seen_random_word_ids"].clear()


def pick_random_unseen_word(user_id: int) -> dict:
    """Случайное слово без повторений в рамках сессии. Сбрасывает историю после полного цикла."""
    state = get_state(user_id)
    seen: set[int] = state["seen_random_word_ids"]
    remaining = [w for w in WORDS if w["id"] not in seen]
    if not remaining:
        seen.clear()
        remaining = WORDS[:]
    word = random.choice(remaining)
    seen.add(word["id"])
    return word

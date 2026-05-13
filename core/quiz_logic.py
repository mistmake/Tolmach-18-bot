import random
import re

from config import QUIZ_OPTIONS_COUNT
from core.storage import WORDS, words_in_category

OUTDATED_MARKERS = (
    "вышло",
    "устарело",
    "не употребляется",
    "архаизм",
    "историзм",
    "изменило значение",
    "сместилось",
)


def is_outdated(word: dict) -> bool:
    today = word["today"].lower()
    return any(marker in today for marker in OUTDATED_MARKERS)


def _shuffle_with_correct(options: list, correct_value) -> tuple[list, int]:
    shuffled = options[:]
    random.shuffle(shuffled)
    return shuffled, shuffled.index(correct_value)


def build_meaning_question() -> dict:
    correct = random.choice(WORDS)
    other_meanings = [w["meaning"] for w in WORDS if w["id"] != correct["id"]]
    distractors = random.sample(other_meanings, QUIZ_OPTIONS_COUNT - 1)
    options_full = [correct["meaning"]] + distractors
    options_full, correct_idx = _shuffle_with_correct(options_full, correct["meaning"])
    return {
        "mode": "meaning",
        "word_id": correct["id"],
        "options_full": options_full,
        "correct_idx": correct_idx,
        "prompt_word": correct["word"],
    }


def _find_word_in_quote(word: str, quote: str) -> tuple[int, int] | None:
    """Возвращает (start, end) первого вхождения слова в цитате или None."""
    pattern = re.compile(re.escape(word), re.IGNORECASE)
    m = pattern.search(quote)
    if m:
        return m.start(), m.end()
    # Эвристика: первые 4–5 букв слова + любое окончание
    stem_len = min(5, max(4, len(word) - 1))
    stem = word[:stem_len]
    if len(stem) >= 4:
        pattern = re.compile(re.escape(stem) + r"\w*", re.IGNORECASE)
        m = pattern.search(quote)
        if m:
            return m.start(), m.end()
    return None


def build_quote_question() -> dict | None:
    attempts = 0
    candidates = WORDS[:]
    random.shuffle(candidates)
    for correct in candidates:
        attempts += 1
        if attempts > 10:
            break
        match = _find_word_in_quote(correct["word"], correct["quote"])
        if not match:
            continue
        start, end = match
        quote_with_blank = correct["quote"][:start] + "_____" + correct["quote"][end:]
        same_cat = [w for w in words_in_category(correct["category"]) if w["id"] != correct["id"]]
        if len(same_cat) >= QUIZ_OPTIONS_COUNT - 1:
            pool = same_cat
        else:
            extra = [w for w in WORDS if w["id"] != correct["id"] and w not in same_cat]
            pool = same_cat + extra
        distractors = random.sample(pool, QUIZ_OPTIONS_COUNT - 1)
        options = [correct["word"]] + [w["word"] for w in distractors]
        options, correct_idx = _shuffle_with_correct(options, correct["word"])
        return {
            "mode": "quote",
            "word_id": correct["id"],
            "options_full": options,
            "correct_idx": correct_idx,
            "quote_with_blank": quote_with_blank,
            "source": correct["source"],
        }
    return None


def build_today_question() -> dict:
    correct = random.choice(WORDS)
    outdated = is_outdated(correct)
    # 0 = "Сохранилось", 1 = "Устарело или изменилось"
    correct_idx = 1 if outdated else 0
    return {
        "mode": "today",
        "word_id": correct["id"],
        "options_full": ["✅ Сохранилось", "❌ Устарело или изменилось"],
        "correct_idx": correct_idx,
        "prompt_word": correct["word"],
        "prompt_meaning": correct["meaning"],
    }


def build_question(mode: str) -> dict | None:
    if mode == "meaning":
        return build_meaning_question()
    if mode == "quote":
        return build_quote_question()
    if mode == "today":
        return build_today_question()
    return None

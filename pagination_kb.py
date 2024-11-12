from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


LEXICON: dict[str, str] = {
    "forward_schedule": "⏩",
    "backward_schedule": "⏪",
    "forward_rating": "⏩",
    "backward_rating": "⏪"
    }


def create_pagination_keyboard(*buttons: str) -> InlineKeyboardMarkup:
    global LEXICON

    kb_builder = InlineKeyboardBuilder()

    kb_builder.row(*[InlineKeyboardButton(text=LEXICON[button] if button in LEXICON else button,
                                          callback_data=button) for button in buttons])

    return kb_builder.as_markup()

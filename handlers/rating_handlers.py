import keyboards.menu_kb as kb
from keyboards.pagination_kb import create_pagination_keyboard

from database import users_data

from lexicon import LEXICON, LEXICON_COMMANDS

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery


router: Router = Router()


@router.message(F.text == LEXICON_COMMANDS["rating"])
async def rating_menu(message: Message):
    await message.answer(LEXICON["rating"], reply_markup=kb.RatingMenu)


@router.message(F.text == LEXICON_COMMANDS["discipline_rating"])
async def send_discipline_rating(message: Message):
    await message.answer(LEXICON["unvailable"])


@router.message(F.text == LEXICON_COMMANDS["short_rating"])
async def send_short_rating(message: Message):
    msg = await message.answer(LEXICON["processing"])
    rating = await users_data[message.chat.id]["rating"].short_disciplines_rating
    await msg.edit_text(rating)


@router.message(F.text == LEXICON_COMMANDS["full_rating"])
async def send_full_rating(message: Message):
    global rating
    global disciplines

    await message.answer(LEXICON["processing"])

    rating = await users_data[message.chat.id]["rating"].full_disciplines_rating
    # disciplines = [i.split(":\n")[0] for i in rating]
    disciplines = [str(i) for i in range(1, len(rating) + 1)]
    page = users_data[message.chat.id]["rating_page"]

    if page != len(disciplines) - 1 and page != 0:

        await message.answer(
            text=rating[page],
            reply_markup=create_pagination_keyboard("backward_rating", disciplines[page], "forward_rating")
            )

    elif page == 0:

        await message.answer(
            text=rating[page], 
            reply_markup=create_pagination_keyboard(disciplines[page], "forward_rating")
            )
    else:

        await message.answer(
            text=rating[page], 
            reply_markup=create_pagination_keyboard("backward_rating", disciplines[page])
            )


@router.callback_query(F.data == "forward_rating")
async def press_forward_rating(callback: CallbackQuery):
    global rating
    global disciplines

    page = users_data[callback.from_user.id]["rating_page"]

    if page + 1 < len(disciplines) - 1:

        await callback.message.edit_text(
            text=rating[page + 1],
            reply_markup=create_pagination_keyboard("backward_rating", disciplines[page + 1], "forward_rating")
            )
    else:

        await callback.message.edit_text(
            text=rating[page + 1],
            reply_markup=create_pagination_keyboard("backward_rating", disciplines[page + 1])
            )

    users_data[callback.from_user.id]["rating_page"] += 1

    await callback.answer()


@router.callback_query(F.data == "backward_rating")
async def press_backward_rating(callback: CallbackQuery):
    global rating
    global disciplines

    page = users_data[callback.from_user.id]["rating_page"]

    if page - 1 > 0:

        await callback.message.edit_text(
            text=rating[page - 1],
            reply_markup=create_pagination_keyboard("backward_rating", disciplines[page - 1], "forward_rating")
            )

    else:

        await callback.message.edit_text(
            text=rating[page - 1],
            reply_markup=create_pagination_keyboard(disciplines[page - 1], "forward_rating")
            )

    users_data[callback.from_user.id]["rating_page"] -= 1

    await callback.answer()
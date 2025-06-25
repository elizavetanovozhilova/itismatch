from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🚀 Давай начнем")]],
    resize_keyboard=True
)

confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Продолжить")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

goal_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="friendship"), KeyboardButton(text="relationship"), KeyboardButton(text="teammate")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

gender_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="M"), KeyboardButton(text="F")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

no_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="нет")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

search_choice_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Найти друга"), KeyboardButton(text="Найти любовь")],
        [KeyboardButton(text="Найти коллегу"), KeyboardButton(text="Поиск по предпочтениям")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

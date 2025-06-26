from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

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
    one_time_keyboard=True)

def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора предпочитаемого пола"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Мужчин", callback_data="pref_gender_M"),
            InlineKeyboardButton(text="Женщин", callback_data="pref_gender_F")
        ],
        [
            InlineKeyboardButton(text="Без разницы", callback_data="pref_gender_any")
        ]
    ])
    return keyboard

def get_specialty_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора предпочитаемой специальности"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Frontend", callback_data="pref_specialty_frontend"),
            InlineKeyboardButton(text="Backend", callback_data="pref_specialty_backend")
        ],
        [
            InlineKeyboardButton(text="iOS", callback_data="pref_specialty_ios"),
            InlineKeyboardButton(text="Android", callback_data="pref_specialty_android")
        ],
        [
            InlineKeyboardButton(text="GameDev", callback_data="pref_specialty_gamedev"),
            InlineKeyboardButton(text="Data Science", callback_data="pref_specialty_data_science")
        ],
        [
            InlineKeyboardButton(text="Project Management", callback_data="pref_specialty_project_management"),
            InlineKeyboardButton(text="UI/UX Design", callback_data="pref_specialty_ui_ux_design")
        ],
        [
            InlineKeyboardButton(text="ML Engineering", callback_data="pref_specialty_ml_engineering"),
            InlineKeyboardButton(text="QA", callback_data="pref_specialty_qa")
        ],
        [
            InlineKeyboardButton(text="Другое", callback_data="pref_specialty_other")
        ],
        [
            InlineKeyboardButton(text="Любая специальность", callback_data="pref_specialty_any")
        ]
    ])
    return keyboard

def get_age_range_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора возрастного диапазона (студенческий возраст)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="18-20", callback_data="pref_age_18_20"),
            InlineKeyboardButton(text="21-23", callback_data="pref_age_21_23")
        ],
        [
            InlineKeyboardButton(text="24-26", callback_data="pref_age_24_26"),
            InlineKeyboardButton(text="18-26", callback_data="pref_age_18_26")
        ],
        [
            InlineKeyboardButton(text="Любой студенческий возраст", callback_data="pref_age_any_any")
        ]
    ])
    return keyboard


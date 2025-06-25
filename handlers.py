from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from keyboards import (
    start_keyboard, confirm_keyboard,
    goal_keyboard, gender_keyboard, no_keyboard, search_choice_keyboard
)
# import asyncpg
from datetime import datetime

router = Router()

# Состояния
class RegisterForm(StatesGroup):
    name = State()
    group = State()
    age = State()
    description = State()
    goal = State()
    gender = State()
    specialty = State()
    photo = State()

# Команда /start
@router.message(F.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer("Привет! Добро пожаловать в нашего бота!", reply_markup=start_keyboard)

# Нажал "Давай начнем"
@router.message(F.text == "🚀 Давай начнем")
async def send_rules(message: types.Message):
    text = (
        "❗️ Помните, что в интернете люди могут выдавать себя за других.\n\n"
        "Бот не запрашивает личные данные и не идентифицирует пользователей по каким-либо документам.\n\n"
        "Продолжая, вы принимаете пользовательское соглашение и политику конфиденциальности."
    )
    await message.answer(text, reply_markup=confirm_keyboard)

# Подтверждение
@router.message(F.text == "✅ Продолжить")
async def ask_name(message: types.Message, state: FSMContext):
    # Удаляем клавиатуру "Продолжить"
    await message.answer("Как тебя зовут?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegisterForm.name)

@router.message(RegisterForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Как называется твоя группа?")
    await state.set_state(RegisterForm.group)

@router.message(RegisterForm.group)
async def process_group(message: types.Message, state: FSMContext):
    await state.update_data(group_name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(RegisterForm.age)

@router.message(RegisterForm.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Расскажи немного о себе или напиши 'нет'", reply_markup=no_keyboard)
    await state.set_state(RegisterForm.description)

@router.message(RegisterForm.description)
async def process_description(message: types.Message, state: FSMContext):
    desc = message.text if message.text.lower() != 'нет' else None
    await state.update_data(description=desc)
    await message.answer(
        "Какая у тебя цель? Выбери одну из кнопок.",
        reply_markup=goal_keyboard
    )
    await state.set_state(RegisterForm.goal)

@router.message(RegisterForm.goal)
async def process_goal(message: types.Message, state: FSMContext):
    goal = message.text.strip().lower()
    if goal not in ['friendship', 'relationship', 'teammate']:
        return await message.answer("Выбери одну из целей: friendship / relationship / teammate", reply_markup=goal_keyboard)
    await state.update_data(goal=goal)
    await message.answer("Укажи свой пол (M / F)", reply_markup=gender_keyboard)
    await state.set_state(RegisterForm.gender)

@router.message(RegisterForm.gender)
async def process_gender(message: types.Message, state: FSMContext):
    gender = message.text.strip().upper()
    if gender not in ['M', 'F']:
        return await message.answer("Пожалуйста, выбери пол: M или F", reply_markup=gender_keyboard)
    await state.update_data(gender=gender)
    await message.answer("Укажи свою специальность", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegisterForm.specialty)

@router.message(RegisterForm.specialty)
async def process_specialty(message: types.Message, state: FSMContext):
    await state.update_data(specialty=message.text)
    await message.answer("Хочешь загрузить фото? Отправь фото или нажми 'нет'", reply_markup=no_keyboard)
    await state.set_state(RegisterForm.photo)

# Вспомогательная функция для показа финальной клавиатуры в зависимости от цели
async def send_final_keyboard(message: types.Message, data: dict):
    goal = data.get('goal')
    if goal == 'friendship':
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Найти друга")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    elif goal == 'relationship':
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Найти любовь")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    elif goal == 'teammate':
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Найти коллегу")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    else:
        keyboard = search_choice_keyboard

    await message.answer("✅ Профиль создан. Спасибо!", reply_markup=keyboard)

@router.message(RegisterForm.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext, db_pool):
    file_id = message.photo[-1].file_id
    await state.update_data(photo=file_id)
    data = await state.get_data()
    await save_user_to_db(message.from_user.id, data, db_pool)
    await send_final_keyboard(message, data)
    await state.clear()

@router.message(RegisterForm.photo)
async def skip_photo(message: types.Message, state: FSMContext, db_pool):
    if message.text.lower() == 'нет':
        await state.update_data(photo=None)
        data = await state.get_data()
        await save_user_to_db(message.from_user.id, data, db_pool)
        await send_final_keyboard(message, data)
        await state.clear()
    else:
        await message.answer("Пожалуйста, отправь фото или нажми 'нет'", reply_markup=no_keyboard)

# Функция сохранения пользователя в БД
async def save_user_to_db(tg_id, data, db_conn):
    await db_conn.execute("""
        INSERT OR IGNORE INTO Users 
        (tg_id, name, group_name, age, description, goal, gender, specialty, photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (tg_id, data['name'], data['group_name'], data['age'],
          data.get('description'), data['goal'], data['gender'],
          data['specialty'], data.get('photo')))
    await db_conn.commit()

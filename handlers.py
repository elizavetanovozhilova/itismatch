from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import get_gender_keyboard, get_specialty_keyboard, get_age_range_keyboard
from db import create_connection
import psycopg2
from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from keyboards import (
    start_keyboard, confirm_keyboard,
    goal_keyboard, gender_keyboard, no_keyboard, search_choice_keyboard
)
from datetime import datetime

preferences_router = Router()

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
    if message.text is None:
        return await message.answer("Пожалуйста, введите описание или 'нет'", reply_markup=no_keyboard)
    desc = message.text if message.text.lower() != 'нет' else None
    await state.update_data(description=desc)
    await message.answer(
        "Какая у тебя цель? Выбери одну из кнопок.",
        reply_markup=goal_keyboard
    )
    await state.set_state(RegisterForm.goal)

@router.message(RegisterForm.goal)
async def process_goal(message: types.Message, state: FSMContext):
    if message.text is None:
        return await message.answer("Выбери одну из целей: friendship / relationship / teammate", reply_markup=goal_keyboard)
    goal = message.text.strip().lower()
    if goal not in ['friendship', 'relationship', 'teammate']:
        return await message.answer("Выбери одну из целей: friendship / relationship / teammate", reply_markup=goal_keyboard)
    await state.update_data(goal=goal)
    await message.answer("Укажи свой пол (M / F)", reply_markup=gender_keyboard)
    await state.set_state(RegisterForm.gender)

@router.message(RegisterForm.gender)
async def process_gender(message: types.Message, state: FSMContext):
    if message.text is None:
        return await message.answer("Пожалуйста, выбери пол: M или F", reply_markup=gender_keyboard)
    gender = message.text.strip().upper()
    if gender not in ['M', 'F']:
        return await message.answer("Пожалуйста, выбери пол: M или F", reply_markup=gender_keyboard)
    await state.update_data(gender=gender)
    await message.answer("Укажи свою специальность", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegisterForm.specialty)

@router.message(RegisterForm.specialty)
async def process_specialty(message: types.Message, state: FSMContext):
    if message.text is None:
        return await message.answer("Пожалуйста, введите специальность")
    await state.update_data(specialty=message.text)
    await message.answer("Хочешь загрузить фото? Отправь фото или нажми 'нет'", reply_markup=no_keyboard)
    await state.set_state(RegisterForm.photo)

# Вспомогательная функция для показа финальной клавиатуры в зависимости от цели
async def send_final_keyboard(message: types.Message, data: dict, state: FSMContext):
    goal = data.get('goal')
    
    # Сначала показываем сообщение о создании профиля
    await message.answer("✅ Профиль создан. Спасибо!")
    
    # Отправляем анкету пользователя
    await send_user_profile(message, data)
    
    # Получаем цель пользователя и запускаем соответствующий flow предпочтений
    if goal == "teammate":
        # Если пользователь ищет тиммейта, сначала спрашиваем специальность
        await state.set_state(PreferencesStates.waiting_for_specialty)
        await message.answer(
            "Отлично! Вы ищете тиммейта для команды.\n\n"
            "Какую специальность вы предпочитаете?",
            reply_markup=get_specialty_keyboard()
        )
    else:
        # Для дружбы и отношений сразу спрашиваем пол
        await state.set_state(PreferencesStates.waiting_for_gender)
        await message.answer(
            "Отлично! Теперь давайте настроим ваши предпочтения для поиска.\n\n"
            "Кого вы хотите найти?",
            reply_markup=get_gender_keyboard()
        )

async def send_user_profile(message: types.Message, data: dict):
    """Отправка анкеты пользователя"""
    goal = data.get('goal')
    if goal is None:
        goal_text = 'Не указано'
    else:
        goal_text = {
            "friendship": "Дружба",
            "relationship": "Отношения", 
            "teammate": "Команда"
        }.get(goal, goal)
    
    gender = data.get('gender')
    if gender is None:
        gender_text = 'Не указано'
    else:
        gender_text = {
            'M': 'Мужской',
            'F': 'Женский'
        }.get(gender, 'Не указано')
    
    description = data.get('description', 'Не указано')
    if description is None:
        description = 'Не указано'
    
    profile_text = f"📋 **Ваша анкета:**\n\n"
    profile_text += f"👤 **Имя:** {data.get('name', 'Не указано')}\n"
    profile_text += f"🎓 **Группа:** {data.get('group_name', 'Не указано')}\n"
    profile_text += f"📅 **Возраст:** {data.get('age', 'Не указано')}\n"
    profile_text += f"👫 **Пол:** {gender_text}\n"
    profile_text += f"🎯 **Цель:** {goal_text}\n"
    profile_text += f"💼 **Специальность:** {data.get('specialty', 'Не указано')}\n"
    profile_text += f"📝 **О себе:** {description}\n"
    
    # Если есть фото, отправляем его с текстом анкеты
    if data.get('photo'):
        await message.answer_photo(
            photo=data['photo'],
            caption=profile_text,
            parse_mode="Markdown"
        )
    else:
        await message.answer(profile_text, parse_mode="Markdown")
    

@router.message(RegisterForm.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    if message.from_user is None or message.photo is None:
        return
    file_id = message.photo[-1].file_id
    await state.update_data(photo=file_id)
    data = await state.get_data()
    await save_user_to_db(message.from_user.id, data)
    await send_final_keyboard(message, data, state)
    await state.clear()

@router.message(RegisterForm.photo)
async def skip_photo(message: types.Message, state: FSMContext):
    if message.from_user is None:
        return
    if message.text is None:
        return await message.answer("Пожалуйста, отправь фото или нажми 'нет'", reply_markup=no_keyboard)
    if message.text.lower() == 'нет':
        await state.update_data(photo=None)
        data = await state.get_data()
        await save_user_to_db(message.from_user.id, data)
        await send_final_keyboard(message, data, state)
        await state.clear()
    else:
        await message.answer("Пожалуйста, отправь фото или нажми 'нет'", reply_markup=no_keyboard)

# Функция сохранения пользователя в БД
async def save_user_to_db(tg_id, data):
    conn = create_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Users 
                (tg_id, name, group_name, age, description, goal, gender, specialty, photo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tg_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    group_name = EXCLUDED.group_name,
                    age = EXCLUDED.age,
                    description = EXCLUDED.description,
                    goal = EXCLUDED.goal,
                    gender = EXCLUDED.gender,
                    specialty = EXCLUDED.specialty,
                    photo = EXCLUDED.photo
            """, (
                tg_id, data['name'], data['group_name'], data['age'],
                data.get('description'), data['goal'], data['gender'],
                data['specialty'], data.get('photo')
            ))
            conn.commit()
            print("Предпочтения успешно сохранены")
            return True
    except psycopg2.Error as e:
        print(f"Ошибка при сохранении пользователя: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# FSM состояния для сбора предпочтений
class PreferencesStates(StatesGroup):
    waiting_for_gender = State()
    waiting_for_specialty = State()  # Только для тиммейтов
    waiting_for_age = State()


@preferences_router.callback_query(StateFilter(PreferencesStates.waiting_for_specialty), F.data.startswith("pref_specialty_"))
async def handle_specialty_preference(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора предпочитаемой специальности (только для тиммейтов)"""
    await callback.answer()  # Подтверждаем нажатие кнопки
    
    specialty = callback.data.split("_")[-1]
    
    # Сохраняем выбор специальности в FSM
    await state.update_data(preferred_specialty=specialty)
    
    # Переходим к выбору пола
    await state.set_state(PreferencesStates.waiting_for_gender)
    
    specialty_text = {
        "frontend": "Frontend",
        "backend": "Backend",
        "ios": "iOS",
        "android": "Android",
        "gamedev": "GameDev",
        "data_science": "Data Science",
        "project_management": "Project Management",
        "ui_ux_design": "UI/UX Design",
        "ml_engineering": "ML Engineering",
        "qa": "QA",
        "other": "Другое",
        "any": "Любая специальность"
    }.get(specialty, specialty)
    
    await callback.message.edit_text(
        f"Специальность: {specialty_text}\n\n"
        "Теперь выберите предпочитаемый пол:",
        reply_markup=get_gender_keyboard()
    )

@preferences_router.callback_query(StateFilter(PreferencesStates.waiting_for_gender), F.data.startswith("pref_gender_"))
async def handle_gender_preference(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора предпочитаемого пола"""
    await callback.answer()  # Подтверждаем нажатие кнопки
    
    gender = callback.data.split("_")[-1]
    
    # Сохраняем выбор пола в FSM
    await state.update_data(preferred_gender=gender)
    
    # Переходим к следующему состоянию
    await state.set_state(PreferencesStates.waiting_for_age)
    
    gender_text = {
        'M': 'Мужчин',
        'F': 'Женщин', 
        'any': 'Без разницы'
    }.get(gender, gender)
    
    await callback.message.edit_text(
        f"Выбрано: {gender_text}\n\n"
        "Выберите предпочитаемый возрастной диапазон:",
        reply_markup=get_age_range_keyboard()
    )

@preferences_router.callback_query(StateFilter(PreferencesStates.waiting_for_age), F.data.startswith("pref_age_"))
async def handle_age_preference(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора возрастного диапазона"""
    await callback.answer()  # Подтверждаем нажатие кнопки
    
    age_data = callback.data.split("_")[-2:]  # Получаем последние два элемента
    
    if age_data[1] == "any":
        min_age = None
        max_age = None
        age_text = "Любой студенческий возраст"
    else:
        min_age = int(age_data[0])
        max_age = int(age_data[1])
        age_text = f"{min_age}-{max_age}"
    
    # Сохраняем возрастной диапазон в FSM
    await state.update_data(min_age=min_age, max_age=max_age)
    
    # Получаем все данные из FSM
    user_data = await state.get_data()
    
    # Получаем цель пользователя
    user_goal = get_user_goal(callback.from_user.id)
    user_data['preferred_goal'] = user_goal
    
    # Сохраняем предпочтения в базу данных
    success = save_user_preferences(callback.from_user.id, user_data)
    
    if success:
        gender_text = {
            'M': 'Мужчин',
            'F': 'Женщин', 
            'any': 'Без разницы'
        }.get(user_data['preferred_gender'], user_data['preferred_gender'])
        
        goal_text = {
            "friendship": "Дружба",
            "relationship": "Отношения", 
            "teammate": "Команда"
        }.get(user_goal, user_goal)
        
        # Формируем сообщение с результатами
        result_text = f"Отлично! Ваши предпочтения сохранены:\n\n"
        result_text += f"Цель: {goal_text}\n"
        result_text += f"Пол: {gender_text}\n"
        result_text += f"Возраст: {age_text}\n"
        
        # Добавляем специальность только если пользователь ищет тиммейта
        if user_goal == "teammate" and user_data.get('preferred_specialty'):
            specialty_text = {
                "frontend": "Frontend",
                "backend": "Backend",
                "ios": "iOS",
                "android": "Android",
                "gamedev": "GameDev",
                "data_science": "Data Science",
                "project_management": "Project Management",
                "ui_ux_design": "UI/UX Design",
                "ml_engineering": "ML Engineering",
                "qa": "QA",
                "other": "Другое",
                "any": "Любая специальность"
            }.get(user_data['preferred_specialty'], user_data['preferred_specialty'])
            result_text += f"Специальность: {specialty_text}\n"
        
        result_text += "\nТеперь вы можете начать поиск!"
        
        await callback.message.edit_text(result_text)
        
        # Очищаем состояние FSM
        await state.clear()
    else:
        await callback.message.edit_text(
            "Произошла ошибка при сохранении предпочтений. Попробуйте еще раз."
        )

def get_user_goal(tg_id: int) -> str:
    """Получение цели пользователя из базы данных"""
    conn = create_connection()
    if not conn:
        return "friendship"  # По умолчанию
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT goal FROM Users WHERE tg_id = %s", (tg_id,))
            row = cursor.fetchone()
            return row[0] if row else "friendship"
    except psycopg2.Error as e:
        print(f"Ошибка при получении цели пользователя: {e}")
        return "friendship"


def save_user_preferences(tg_id: int, preferences: dict) -> bool:
    """Сохранение предпочтений пользователя в базу данных"""
    print(f"DEBUG: Попытка сохранения предпочтений для tg_id: {tg_id}")
    print(f"DEBUG: Данные предпочтений: {preferences}")
    
    conn = create_connection()
    if not conn:
        print("DEBUG: Ошибка подключения к базе данных")
        return False
    
    try:
        with conn.cursor() as cursor:
            # Получаем user_id по tg_id
            cursor.execute("SELECT user_id FROM Users WHERE tg_id = %s", (tg_id,))
            user_row = cursor.fetchone()
            if not user_row:
                print(f"DEBUG: Пользователь с tg_id {tg_id} не найден")
                return False
            
            user_id = user_row[0]
            print(f"DEBUG: Найден user_id: {user_id}")
            
            # Сохраняем предпочтения
            cursor.execute("""
                INSERT INTO User_Preferences 
                (user_id, preferred_gender, min_age, max_age, preferred_goal, preferred_specialty)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    preferred_gender = EXCLUDED.preferred_gender,
                    min_age = EXCLUDED.min_age,
                    max_age = EXCLUDED.max_age,
                    preferred_goal = EXCLUDED.preferred_goal,
                    preferred_specialty = EXCLUDED.preferred_specialty
            """, (
                user_id,
                preferences.get("preferred_gender"),
                preferences.get("min_age"),
                preferences.get("max_age"),
                preferences.get("preferred_goal"),
                preferences.get("preferred_specialty")
            ))
            
            conn.commit()
            print("DEBUG: Предпочтения успешно сохранены")
            return True
            
    except psycopg2.Error as e:
        print(f"DEBUG: Ошибка при сохранении предпочтений: {e}")
        print(f"DEBUG: Код ошибки: {e.pgcode}")
        print(f"DEBUG: Сообщение: {e.pgerror}")
        conn.rollback()
        return False
    finally:
        conn.close()


@preferences_router.message(Command("mystate"))
async def debug_state(message: types.Message, state: FSMContext):
    current = await state.get_state()
    await message.answer(f"Ваше текущее состояние: {current}")

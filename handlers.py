from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import get_gender_keyboard, get_specialty_keyboard, get_age_range_keyboard
from db import create_connection
import psycopg2

preferences_router = Router()

# FSM состояния для сбора предпочтений
class PreferencesStates(StatesGroup):
    waiting_for_gender = State()
    waiting_for_specialty = State()  # Только для тиммейтов
    waiting_for_age = State()

@preferences_router.message(Command("start_preferences"))
async def start_preferences(message: Message, state: FSMContext):
    """Начало сбора предпочтений пользователя"""
    # Получаем цель пользователя из базы данных
    user_goal = get_user_goal(message.from_user.id)
    
    if user_goal == "teammate":
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

@preferences_router.callback_query(StateFilter(PreferencesStates.waiting_for_specialty), F.data.startswith("pref_specialty_"))
async def handle_specialty_preference(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора предпочитаемой специальности (только для тиммейтов)"""
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
    gender = callback.data.split("_")[-1]
    
    # Сохраняем выбор пола в FSM
    await state.update_data(preferred_gender=gender)
    
    # Переходим к следующему состоянию
    await state.set_state(PreferencesStates.waiting_for_age)
    
    await callback.message.edit_text(
        f"Выбрано: {'Мужчин' if gender == 'M' else 'Женщин' if gender == 'F' else 'Без разницы'}\n\n"
        "Выберите предпочитаемый возрастной диапазон:",
        reply_markup=get_age_range_keyboard()
    )

@preferences_router.callback_query(StateFilter(PreferencesStates.waiting_for_age), F.data.startswith("pref_age_"))
async def handle_age_preference(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора возрастного диапазона"""
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
    finally:
        conn.close()

def save_user_preferences(tg_id: int, preferences: dict) -> bool:
    """Сохранение предпочтений пользователя в базу данных"""
    conn = create_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            # Получаем user_id по tg_id
            cursor.execute("SELECT user_id FROM Users WHERE tg_id = %s", (tg_id,))
            user_row = cursor.fetchone()
            if not user_row:
                return False
            
            user_id = user_row[0]
            
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
            return True
            
    except psycopg2.Error as e:
        print(f"Ошибка при сохранении предпочтений: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

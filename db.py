import aiosqlite
import asyncio

DB_FILE = "local_database.sqlite"

async def create_pool():
    # В sqlite "пул" - это просто соединение к файлу БД
    conn = await aiosqlite.connect(DB_FILE)
    await create_tables(conn)
    return conn

async def create_tables(conn):
    await conn.executescript("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            group_name TEXT,
            age INTEGER,
            description TEXT,
            photo BLOB,
            goal TEXT NOT NULL,
            gender TEXT NOT NULL,
            specialty TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS Likes (
            like_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            like_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_mutual BOOLEAN DEFAULT 0,
            UNIQUE(sender_id, receiver_id),
            FOREIGN KEY(sender_id) REFERENCES Users(user_id),
            FOREIGN KEY(receiver_id) REFERENCES Users(user_id)
        );

        CREATE TABLE IF NOT EXISTS Profile_Views (
            view_id INTEGER PRIMARY KEY AUTOINCREMENT,
            viewer_id INTEGER NOT NULL,
            viewed_id INTEGER NOT NULL,
            view_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(viewer_id, viewed_id),
            FOREIGN KEY(viewer_id) REFERENCES Users(user_id),
            FOREIGN KEY(viewed_id) REFERENCES Users(user_id)
        );

        CREATE TABLE IF NOT EXISTS Reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_id INTEGER,
            reported_user_id INTEGER,
            reason TEXT,
            report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(reporter_id) REFERENCES Users(user_id),
            FOREIGN KEY(reported_user_id) REFERENCES Users(user_id)
        );

        CREATE TABLE IF NOT EXISTS User_Preferences (
            preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            preferred_gender TEXT,
            min_age INTEGER,
            max_age INTEGER,
            preferred_goal TEXT,
            preferred_specialty TEXT,
            FOREIGN KEY(user_id) REFERENCES Users(user_id)
        );
    """)
    await conn.commit()

import psycopg2
from psycopg2 import OperationalError

def create_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="itismatch",
            user="postgres",
            password="1"
        )
        return conn
    except OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

create_connection()
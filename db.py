import sqlite3
import logging

DB_NAME = "users.db"


# ================= INIT DB =================
def init_db():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY
                )
            """
            )
            conn.commit()
    except Exception as e:
        logging.error(f"DB init error: {e}")


# ================= ADD USER =================
def add_user(user_id: int):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
                (user_id,),
            )
            conn.commit()
    except Exception as e:
        logging.error(f"Add user error: {e}")


# ================= GET USERS =================
def get_all_users():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users")
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Get users error: {e}")
        return []


# ================= REMOVE USER =================
def remove_user(user_id: int):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
    except Exception as e:
        logging.error(f"Remove user error: {e}")

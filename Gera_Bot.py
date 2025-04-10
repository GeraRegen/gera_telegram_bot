import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import sqlite3
from sqlite3 import Error



# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Имя файла базы данных
DB_FILE = "members.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)

# ========== РАБОТА С БАЗОЙ ДАННЫХ ==========
def create_connection():
    """Создаёт соединение с SQLite базой данных"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except Error as e:
        logger.error(f"Ошибка подключения к SQLite: {e}")
    return conn


def init_db():
    """Создаёт таблицу, если она не существует"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    chat_id INTEGER,
                    nickname TEXT,
                    UNIQUE(chat_id, nickname)
                )
            """)
            conn.commit()
        except Error as e:
            logger.error(f"Ошибка при создании таблицы: {e}")
        finally:
            conn.close()


def add_member(chat_id: int, nickname: str):
    """Добавляет участника в базу данных"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO members VALUES (?, ?)", (chat_id, nickname))
            conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            logger.error(f"Ошибка при добавлении участника: {e}")
            return False
        finally:
            conn.close()
    return False


def get_members(chat_id: int):
    """Возвращает список участников для указанного чата"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT nickname FROM members WHERE chat_id = ?", (chat_id,))
            return [row[0] for row in cursor.fetchall()]
        except Error as e:
            logger.error(f"Ошибка при получении участников: {e}")
            return []
        finally:
            conn.close()
    return []


# ========== КОМАНДЫ БОТА ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    help_text = (
        "🤖 Бот для учета участников команды\n\n"
        "Доступные команды:\n"
        "/add [Имя Фамилия] - добавить участника\n"
        "/members - показать список участников"
    )
    await update.message.reply_text(help_text)


async def add_nick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление участника: /add Иван Петров"""
    chat_id = update.message.chat_id
    args = context.args

    if not args:
        await update.message.reply_text("❌ Укажите имя: /add Иван Петров")
        return

    nickname = " ".join(args)

    if add_member(chat_id, nickname):
        await update.message.reply_text(f"✅ {nickname} добавлен в список участников!")
    else:
        await update.message.reply_text(f"⚠️ {nickname} уже есть в списке!")


async def show_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать участников: /members"""
    chat_id = update.message.chat_id
    members = get_members(chat_id)

    if not members:
        await update.message.reply_text("📭 Список участников пуст.")
    else:
        members_list = "\n".join(f"👤 {nick}" for nick in members)
        await update.message.reply_text(f"📋 Участники ({len(members)}):\n{members_list}")


# ========== ЗАПУСК БОТА ==========
def main():
    # Инициализация базы данных
    init_db()

    # Создаём приложение бота
    app = Application.builder().token("7762254781:AAEtTStYgmDmJ676XLgxxEGG0vL0xxHHV0E").build()

    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_nick))
    app.add_handler(CommandHandler("members", show_members))

    # Запускаем бота
    app.run_polling()


if __name__ == "__main__":
    main()

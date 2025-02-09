import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from tokenza import TOKEN

# Database connection
def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    return conn

def get_table_schema(db_path):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({db_path});")
    columns = cursor.fetchall()
    conn.close()
    schema_info = "\n".join([f"{col[1]} ({col[2]})" for col in columns])
    return schema_info

def get_random_question(db_path='questions.db'):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT question_text, query, difficulty, db_name FROM sql_questions ORDER BY RANDOM() LIMIT 1;")
    question = cursor.fetchone()
    conn.close()
    return question

async def send_question(update: Update, context: CallbackContext):
    question = get_random_question()
    if question:
        question_text, _, difficulty, table_name = question
        table_schema = get_table_schema(table_name)
        await update.message.reply_text(f"🔹 Difficulty: {difficulty}\n📊 Table Schema:\n{table_schema}\n❓ {question_text}")
    else:
        await update.message.reply_text("No questions available.")

async def check_answer(update: Update, context: CallbackContext):
    user_query = update.message.text
    conn = get_db_connection('questions.db')
    cursor = conn.cursor()
    cursor.execute("SELECT query FROM sql_questions ORDER BY RANDOM() LIMIT 1;")
    correct_query = cursor.fetchone()
    conn.close()

    if correct_query and user_query.strip().lower() == correct_query[0].strip().lower():
        await update.message.reply_text("✅ Correct answer!")
    else:
        await update.message.reply_text(f"❌ Incorrect! The correct answer was: \n{correct_query[0]}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", send_question))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

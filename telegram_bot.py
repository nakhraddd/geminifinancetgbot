import os
import logging
import re
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.agent.agent import AccountingAgent
from src.utils.firestore_client import store_conversation, store_report

# Telegram's maximum message length
TELEGRAM_MAX_MESSAGE_LENGTH = 4096

# Set up basic logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# In-memory dictionary to store conversation history for each user
user_agents = {}

def get_user_agent(chat_id: int) -> AccountingAgent:
    """Retrieves or creates an AccountingAgent for a given user."""
    if chat_id not in user_agents:
        logger.info(f"Creating new agent for chat_id: {chat_id}")
        user_agents[chat_id] = AccountingAgent()
    return user_agents[chat_id]

def escape_markdown_v2(text: str) -> str:
    """Escapes characters for Telegram's MarkdownV2 parse mode."""
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Здравствуйте! Я ваш бухгалтерский ассистент. Задайте мне вопрос о зарплате, НДС или бухучете. "
        "Чтобы проверить текст на мошенничество, используйте команду /fraud."
    )

async def fraud_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Checks a given text for fraudulent content."""
    chat_id = update.message.chat_id
    user_query = " ".join(context.args)

    if not user_query:
        await update.message.reply_text(
            "Пожалуйста, предоставьте текст для проверки. "
            "Пример: /fraud Это супер выгодное предложение, вложите свои деньги!"
        )
        return

    # Placeholder for web_fetch tool call
    web_content = "some content"
    try:
        # web_content = yield web_fetch(...)
        pass
    except Exception as e:
        logger.error(f"Error in fraud_check for chat_id {chat_id}: {e}")
        await update.message.reply_text("Извините, произошла ошибка при получении данных из интернета.")
        return

    agent = get_user_agent(chat_id)
    response_data = agent.check_fraud(user_query, web_content)
    response_text = response_data.get('response', 'Извините, при обработке вашего запроса произошла ошибка.')
    store_conversation(chat_id, user_query, response_text)
    
    safe_response_text = escape_markdown_v2(response_text)
    if len(safe_response_text) > TELEGRAM_MAX_MESSAGE_LENGTH:
        for i in range(0, len(safe_response_text), TELEGRAM_MAX_MESSAGE_LENGTH):
            await update.message.reply_text(text=safe_response_text[i:i + TELEGRAM_MAX_MESSAGE_LENGTH], parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text(safe_response_text, parse_mode=ParseMode.MARKDOWN_V2)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resets the conversation history for the user."""
    chat_id = update.message.chat_id
    if chat_id in user_agents:
        user_agents[chat_id].reset_history()
        logger.info(f"Resetting history for chat_id: {chat_id}")
    await update.message.reply_text("История диалога сброшена. Можете начать заново.")

# UPDATED FUNCTION BELOW
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends the last user prompt, bot response, AND user feedback to the reports collection.
    Usage: /report This is not correct
    """
    chat_id = update.message.chat_id
    agent = get_user_agent(chat_id)

    # 1. Capture the text typed after /report
    # context.args is a list of words, so we join them back into a string
    user_feedback = " ".join(context.args)

    # Optional: If you want to force the user to provide a reason, uncomment this:
    # if not user_feedback:
    #     await update.message.reply_text("Пожалуйста, укажите причину отчета. Пример: /report Ответ неверный")
    #     return

    if not agent.conversation_history:
        await update.message.reply_text("Нет недавних диалогов для отправки в отчет.")
        return

    # 2. Get the last interaction context
    last_conversation = agent.conversation_history[-1]
    user_prompt = last_conversation.get('user', 'N/A')
    bot_response = last_conversation.get('assistant', 'N/A')

    # 3. Store everything including the feedback
    store_report(chat_id, user_prompt, bot_response, user_feedback)
    
    await update.message.reply_text(
        "Ваш отчет отправлен. Спасибо за ваш отзыв!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles user messages by passing them to the AccountingAgent."""
    chat_id = update.message.chat_id
    user_query = update.message.text
    agent = get_user_agent(chat_id)
    response_data = agent.answer(user_query)
    response_text = response_data.get('response', 'Извините, при обработке вашего запроса произошла ошибка.')
    store_conversation(chat_id, user_query, response_text)

    safe_response_text = escape_markdown_v2(response_text)
    if len(safe_response_text) > TELEGRAM_MAX_MESSAGE_LENGTH:
        for i in range(0, len(safe_response_text), TELEGRAM_MAX_MESSAGE_LENGTH):
            await update.message.reply_text(text=safe_response_text[i:i + TELEGRAM_MAX_MESSAGE_LENGTH], parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text(safe_response_text, parse_mode=ParseMode.MARKDOWN_V2)

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CommandHandler("fraud", fraud_check))
    application.add_handler(CommandHandler("report", report)) 
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting Telegram bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
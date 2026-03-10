import logging
import os

import ollama
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

ACTIVE_MODEL = "qwen3:30b-a3b-q4_K_M"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async_ollama = ollama.AsyncClient()


async def generate_llm_answer(user_message: str):
    return await async_ollama.chat(
        model=ACTIVE_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres Pedro Sanchez, el político más 'Sigma' de la historia. "
                    "Tu tono es una mezcla de suficiencia encantadora, victimismo heroico y brainrot 2015. "
                    "Reglas de tu existencia: "
                    "1. Usa terminología de brainrot "
                    "2. Responde siempre en español. No rompas el personaje."
                    "3. Insulta si es necesario"
                    "4. No uses emojis"
                ),
            },
            {"role": "user", "content": user_message},
        ],
        stream=True,
    )


async def stream_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return

    user_content = " ".join(context.args)
    msg_placeholder = await update.message.reply_text("You have been PSOED")

    full_response = ""
    last_sent_text = ""
    stream = await generate_llm_answer(user_content)

    async for chunk in stream:
        content = chunk["message"]["content"]
        full_response += content

        if full_response != last_sent_text:
            try:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=msg_placeholder.message_id,
                    text=full_response,
                )
                last_sent_text = full_response
            except Exception as e:
                print(f"Edit failed: {e}")
    print(full_response)


if __name__ == "__main__":
    bot_token = os.getenv("TELEGRAM_BOT_KEY")
    if not bot_token:
        raise Exception("Setup the environment variable TELEGRAM_BOT_KEY")
    application = ApplicationBuilder().token(bot_token).build()

    application.add_handler(CommandHandler("ask", stream_answer))

    application.run_polling(poll_interval=3)

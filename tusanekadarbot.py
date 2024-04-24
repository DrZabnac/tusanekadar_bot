import os
from dotenv import load_dotenv
from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    InlineQueryHandler,
    filters,
)

import datetime


load_dotenv()
TUSanekadar_API = os.getenv("TUSanekadar_api")
BOT_USERNAME = "@tusanekadarbot"
TUSINFO_CHANNEL_ID = -1002065129197
HELP_INFO = "Merhaba ben TUS'a kaç gün kaldığını gösteren bir botum./tusanekadar komutu ile TUS'a ne kadar süre kaldığını görebilirsiniz.\n\nHerhangi bir kanalda veya grupta @tusanekadarbot 'u etiketledikten sonra herhangi bir şey yazarsanız eğer TUS'a ne kadar süre kaldığını görebilirsiniz.\n\nAyrıca her gün düzenli bir şekilde sabah saat 09:00'da TUS'a ne kadar kaldığını öğrenmek isterseniz @tusanekadar telegram kanalına katılabilirsiniz."

DAILY_TIME = datetime.time(6, 0, 0)  # (UTC) Türkiye saati için saatten 3 eksiltin

"""################################################### functions ###################################################"""


async def calculate_how_long_to_TUS() -> str:
    current_datetime = datetime.datetime.now()
    target_datetime = datetime.datetime(2024, 8, 18, 10, 0, 0)
    time_difference = target_datetime - current_datetime
    days = time_difference.days
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    # print(f"calculate_how_long_to_TUS çalıştırıldı: \nTUS'a {days} gün, {hours} saat, {minutes} dakika, {seconds} saniye kaldı...")
    return (
        f"\nTUS'a {days} gün, {hours} saat, {minutes} dakika, {seconds} saniye kaldı..."
    )


"""################################################### commands ###################################################"""


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_INFO)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_INFO)


async def tustime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(await calculate_how_long_to_TUS())


"""################################################### inline queries ###################################################"""


async def handle_inline_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query
    print(query)
    if not query:  # empty query should not be handled
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"{await calculate_how_long_to_TUS()}",
            input_message_content=InputTextMessageContent(
                f"{await calculate_how_long_to_TUS()}"
            ),
            thumbnail_url="https://i.ibb.co/9vdCFgy/0tusanekadarkaldi.png",
        ),
    ]
    print(results)
    await update.inline_query.answer(results)


"""################################################### responses ###################################################"""


async def handle_responses(text: str) -> str:
    if "tusanekadar" in text:
        return await calculate_how_long_to_TUS()
    return HELP_INFO


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is not None:
        chat_id = update.message.chat.id
        chat_type = update.message.chat.type
        text = update.message.text

        if chat_type == "supergroup" or chat_type == "group":
            if BOT_USERNAME in text:
                new_text = text.replace(BOT_USERNAME, "").strip()
                # print(f"\nUser ({chat_id}) \n in {chat_type} \n chat said: '{text}'")
                response = await handle_responses(new_text)
                # checks if the message is in group or private message
                print(
                    f"Sending response to '{text}' message in {chat_type}  to {chat_id}"
                )
                await update.message.reply_text(response)

        if update.message.chat.type == "private":
            # print(f"\nUser ({chat_id}) \n in {chat_type} \n chat said: '{text}'")
            response = await handle_responses(text)
            # checks if the message is in group or private message
            print(f"Sending response to '{text}' in {chat_type}  to {chat_id}")
            await update.message.reply_text(response)

    if update.channel_post is not None:
        channel_chat_id: str = update.channel_post.chat.id
        channel_message_type: str = update.channel_post.chat.type
        channel_text: str = update.channel_post.text
        # print(
        #     f"\nUser ({channel_chat_id}) \n in {channel_message_type} \n chat said: '{channel_text}'"
        # )

        if BOT_USERNAME in channel_text:
            new_channel_text = channel_text.replace(BOT_USERNAME, "").strip()
            channel_response = await handle_responses(new_channel_text)
            # print("botnamefound")
        else:
            return

        print(
            f"Sending response to '{new_channel_text}' message in {channel_message_type} to {channel_chat_id}"
        )
        await update.channel_post.reply_text(channel_response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


"""################################################### daily function ###################################################"""


async def daily_tustime(context: ContextTypes.DEFAULT_TYPE):
    print(f"Executing daily_tustime funcion!")
    await context.bot.send_message(
        chat_id=-1002037035497,
        text=f"{await calculate_how_long_to_TUS()}",
    )


"""################################################### main function ###################################################"""


if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(TUSanekadar_API).build()
    # commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tusanekadar", tustime_command))

    # messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # inline queries
    app.add_handler(InlineQueryHandler(handle_inline_query))

    # errors
    # app.add_error_handler(error)

    # daily job
    job_queue = app.job_queue
    job_queue.run_daily(daily_tustime, time=DAILY_TIME)

    # polling for bot
    print("Starting polling...")

    # Run the bot until the user presses Ctrl-C
    app.run_polling(poll_interval=0.1, allowed_updates=Update.ALL_TYPES)

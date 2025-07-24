#
# A Telegram bot to download audio from YouTube & YouTube Music links.
#

import logging
import os
import requests
import asyncio
from dotenv import load_dotenv

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1

# --- Initial Setup ---

# Load environment variables from the .env file
load_dotenv()

# Get the bot token from the environment variable. This is safer than hard-coding it.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables!")

# Set up logging to see what the bot is doing and catch errors.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- Bot Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command with a welcome message."""
    user = update.effective_user
    # User-facing text in Turkish, as requested.
    await update.message.reply_html(rf"Selam {user.mention_html()}! 👋")
    await update.message.reply_text("Selamlar, bana bir youtube msuic linki at sarkiyi indireyim.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes incoming text messages to find and download YouTube links."""
    message_text = update.message.text

    # 1. Validate the link to ensure it's a YouTube URL.
    if 'youtube.com/' not in message_text and 'youtu.be/' not in message_text:
        await update.message.reply_text("gecerli link at oc.")
        return

    processing_message = await update.message.reply_text("Heh tmm oldu bekle 🎶\Indiriom sarkiyi.")

    downloaded_file_path = None
    try:
        # 2. Download the audio using yt-dlp.
        # We configure it to get the best audio, convert it to a 192kbps MP3,
        # and name the file with its unique video ID to avoid naming conflicts.
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first to get metadata before the full download.
            info_dict = ydl.extract_info(message_text, download=False)
            video_id = info_dict.get('id')
            video_title = info_dict.get('title', 'Unknown Title')
            artist = info_dict.get('artist', 'Unknown Artist')
            thumbnail_url = info_dict.get('thumbnail')
            
            # Now, perform the actual download and conversion.
            ydl.download([message_text])
            downloaded_file_path = f"{video_id}.mp3"

        # 3. Embed metadata into the MP3 file using Mutagen.
        audio = MP3(downloaded_file_path, ID3=ID3)
        if audio.tags is None:
            audio.add_tags()

        audio.tags.add(TIT2(encoding=3, text=video_title))
        audio.tags.add(TPE1(encoding=3, text=artist))

        # Download the thumbnail and embed it as cover art.
        if thumbnail_url:
            response = requests.get(thumbnail_url)
            if response.status_code == 200:
                audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=response.content))
        
        audio.save()
        logger.info(f"Metadata embedded for '{video_title}'")
        
        # 4. Send the final MP3 file to the user.
        caption_text = f'<a href="https://t.me/racistdawg">Made By</a> | <a href="{message_text}">Originak Song</a>'
        
        with open(downloaded_file_path, 'rb') as audio_file:
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=audio_file,
                caption=caption_text,
                parse_mode=ParseMode.HTML,
                title=video_title,
                performer=artist,
                filename=f"{artist} - {video_title}.mp3"
            )
        
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_message.message_id)

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        await context.bot.edit_message_text(
            text=f"Sorry, something went wrong. 😔\nError: {e}",
            chat_id=update.effective_chat.id,
            message_id=processing_message.message_id
        )

    finally:
        # 5. Clean up by deleting the downloaded file from the server.
        if downloaded_file_path and os.path.exists(downloaded_file_path):
            os.remove(downloaded_file_path)
            logger.info(f"Cleaned up file: {downloaded_file_path}")


def main() -> None:
    """Initializes and runs the bot application."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # The `async with` block ensures the application is properly initialized and shut down.
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        print("Bot is running... Press Ctrl-C to stop.")
        
        # Keep the script running until manually stopped.
        await asyncio.Event().wait()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")

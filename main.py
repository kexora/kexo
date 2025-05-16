import os
import yt_dlp
import logging
from telegram import Update, ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Token from environment variable

DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me any Instagram public video/reel/story link.")

def download_instagram_video(url: str) -> str:
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title).50s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'merge_output_format': 'mp4',
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "instagram.com" not in url:
        await update.message.reply_text("⚠️ Please send a valid Instagram link.")
        return

    await update.message.chat.send_action(ChatAction.UPLOAD_VIDEO)
    await update.message.reply_text("🔄 Downloading video, please wait...")

    try:
        video_path = download_instagram_video(url)
        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file)
        os.remove(video_path)
    except Exception as e:
        logging.error(f"Download failed: {e}")
        await update.message.reply_text("❌ Download failed. Make sure the link is public.")

def main():
    token = BOT_TOKEN
    if not token:
        print("❌ Error: BOT_TOKEN environment variable not set.")
        return

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

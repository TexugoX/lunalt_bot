import os
import tempfile
from threading import Thread
import yt_dlp
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Token do seu bot do Telegram
TELEGRAM_TOKEN = "7852526231:AAH12wUiYwJhlzktoa1CXC5azi9cLJmTY94"

# --- MINI SERVIDOR WEB (Necessário para o Render manter o Web Service gratuito ativo) ---
app_web = Flask(__name__)


@app_web.route("/")
def home():
  return "Lunalt Bot está online e rodando!"


def run_web():
  port = int(os.environ.get("PORT", 10000))
  app_web.run(host="0.0.0.0", port=port)


# --- LÓGICA DO BOT DO TELEGRAM ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  url = update.message.text.strip()

  if not url.startswith("http"):
    await update.message.reply_text(
        "Por favor, envie um link válido (começando com http:// ou https://)."
    )
    return

  processing_msg = await update.message.reply_text(
      "O **Lunalt** está baixando para você... ⏳"
  )

  output_dir = os.path.join(tempfile.gettempdir(), "lunalt_downloads")
  os.makedirs(output_dir, exist_ok=True)

  ydl_opts = {
      "format": "mp4/best",
      "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
      "max_filesize": 50 * 1024 * 1024,  # Limite de 50MB do Telegram
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      filename = ydl.prepare_filename(info)

    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=open(filename, "rb"),
        caption="✅ **Download concluído com sucesso pelo Lunalt! 😎**",
        parse_mode="Markdown",
    )

    os.remove(filename)
    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=processing_msg.message_id
    )

  except yt_dlp.utils.DownloadError:
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=processing_msg.message_id,
        text=(
            "❌ O Lunalt não conseguiu baixar este link. O arquivo pode ser"
            " muito grande (>50MB) ou protegido."
        ),
    )
  except Exception as e:
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=processing_msg.message_id,
        text=f"⚠️ Ocorreu um erro: {e}",
    )


def main():
  # Inicia o mini servidor web em segundo plano para o Render
  t = Thread(target=run_web)
  t.start()

  # Inicializa o bot do Telegram
  app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
  app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

  print("Lunalt rodando com suporte Web...")
  app.run_polling()


if __name__ == "__main__":
  main()
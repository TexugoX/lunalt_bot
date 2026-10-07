import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Token do seu bot do Telegram
TELEGRAM_TOKEN = "7852526231:AAH12wUiYwJhlzktoa1CXC5azi9cLJmTY94"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  url = update.message.text.strip()

  # Validação simples de link
  if not url.startswith("http"):
    await update.message.reply_text(
        "Por favor, envie um link válido (começando com http:// ou https://)."
    )
    return

  processing_msg = await update.message.reply_text(
      "O **Lunalt** está baixando o arquivo para você... ⏳"
  )

  output_dir = "downloads"
  os.makedirs(output_dir, exist_ok=True)

  # Configurações do yt-dlp para baixar o melhor formato compatível
  ydl_opts = {
      "format": "mp4/best",
      "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
      "max_filesize": 50
      * 1024
      * 1024,  # Limite de 50MB (limite padrão para envio via bot gratuito do Telegram)
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      # Extrai informações e baixa o arquivo
      info = ydl.extract_info(url, download=True)
      filename = ydl.prepare_filename(info)

    # Envia o arquivo de vídeo/mídia diretamente no chat
    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=open(filename, "rb"),
        caption=(
            "✅ **Download concluído com sucesso pelo Lunalt!**"
        ),
        parse_mode="Markdown",
    )

    # Apaga o arquivo do computador para não ocupar espaço
    os.remove(filename)
    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=processing_msg.message_id
    )

  except yt_dlp.utils.DownloadError as e:
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
  app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
  app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

  print("Lunalt (yt-dlp) rodando... Pressione Ctrl+C para parar.")
  app.run_polling()


if __name__ == "__main__":
  main()
import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask
from threading import Thread

TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 10000))

# Servidor Keep-Alive (Obrigatório para 24/7 no Render)
app = Flask(__name__)
@app.route('/')
def health_check():
    return "🤖 Bot TikTok Online - Wellington"

# Teclado personalizado
def get_main_menu():
    return ReplyKeyboardMarkup(
        [['🎬 Baixar Vídeo TikTok'], ['❔ Ajuda']],
        resize_keyboard=True,
        one_time_keyboard=False  # Alterado para False para melhor UX
    )

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        """🎬 *Baixador de Vídeos do TikTok*

Escolha uma opção:
1. 🎬 Baixar Vídeo TikTok
2. ❔ Ajuda

🔧 Criado por: Wellington""",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        """🤖 *Como usar o robô baixador de vídeos?*

1. Envie um link do TikTok que eu baixo e te envio de volta.
2. Lembre-se você é o único (a) responsável pelo seu sucesso.

Você entendeu? (Responda 'sim' ou 'não')""",
        parse_mode="Markdown"
    )
    return "AGUARDANDO_CONFIRMACAO"

def handle_confirmation(update: Update, context: CallbackContext):
    if update.message.text.lower() in ['sim', 's', 'yes', 'y']:
        update.message.reply_text("✅ Envie o link do vídeo:", reply_markup=get_main_menu())
    else:
        update.message.reply_text("❌ Revise as instruções e tente novamente.", reply_markup=get_main_menu())
    return -1

def download_video(url):
    try:
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=15).json()  # Aumentado timeout
        return response["data"]["play"] if response.get("code") == 0 else None
    except:
        return None

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    
    if text == '🎬 Baixar Vídeo TikTok':
        update.message.reply_text("📤 Envie o link do TikTok:")
        return "AGUARDANDO_LINK"
        
    elif text == '❔ Ajuda':
        return help_command(update, context)
        
    elif "tiktok.com" in text:
        update.message.reply_text("⏳ Processando...")
        if video_url := download_video(text):
            update.message.reply_video(
                video_url,
                caption="✅ Baixado via @baixador_videos_tiktokbot",
                reply_markup=get_main_menu()
            )
        else:
            update.message.reply_text("❌ Link inválido. Tente outro.", reply_markup=get_main_menu())
        return -1
    else:
        update.message.reply_text("⚠️ Use os botões ou envie um link.", reply_markup=get_main_menu())

def main():
    # Inicia servidor web em thread separada
    Thread(target=lambda: app.run(host='0.0.0.0', port=PORT)).start()
    
    # Configuração segura do bot
    updater = Updater(TOKEN, use_context=True)
    updater.bot.delete_webhook(drop_pending_updates=True)  # Limpa atualizações antigas
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ajuda", help_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🚀 Bot iniciado com sucesso!")
    updater.start_polling(
        drop_pending_updates=True,  # Ignora mensagens pendentes
        timeout=30,  # Tempo de espera por updates
        allowed_updates=['message']  # Filtra tipos de update
    )
    updater.idle()

if __name__ == "__main__":
    main()

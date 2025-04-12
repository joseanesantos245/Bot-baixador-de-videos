import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("TELEGRAM_TOKEN")

# Teclado personalizado
def get_main_menu():
    return ReplyKeyboardMarkup(
        [['🎬 Baixar Vídeo TikTok'], ['❔ Ajuda']],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def start(update: Update, context: CallbackContext):
    mensagem = """
    🎬 *Baixador de Vídeos do TikTok*

Escolha uma opção abaixo:

1. 🎬 Baixar Vídeo TikTok
Envie qualquer link do TikTok que eu baixo e te envio de volta.

2. ❔ Ajuda
Tire suas dúvidas sobre como usar

🔧 Criado por: Wellington
    """
    update.message.reply_text(
        mensagem,
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

def help_command(update: Update, context: CallbackContext):
    ajuda_msg = """
🤖 *Como usar o robô baixador de vídeos?*

1. Envie um link do TikTok que eu baixo e te envio de volta.
2. Lembre-se você é o único (a) responsável pelo seu futuro.

Você entendeu? (Responda 'sim' ou 'não')
    """
    update.message.reply_text(
        ajuda_msg,
        parse_mode="Markdown"
    )
    return "AGUARDANDO_CONFIRMACAO"

def handle_confirmation(update: Update, context: CallbackContext):
    resposta = update.message.text.lower()
    if resposta in ['sim', 's', 'yes', 'y']:
        update.message.reply_text(
            "Ótimo! Agora envie o link do vídeo que deseja baixar.",
            reply_markup=get_main_menu()
        )
    else:
        update.message.reply_text(
            "Por favor, leia as instruções com atenção e tente novamente.",
            reply_markup=get_main_menu()
        )
    return -1  # Volta para o menu principal

def download_video(url):
    try:
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=10).json()
        if response.get("code") == 0:
            return response["data"]["play"]
    except:
        return None

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    
    if text == '🎬 Baixar Vídeo TikTok':
        update.message.reply_text("Por favor, envie o link do vídeo do TikTok:")
        return "AGUARDANDO_LINK"
        
    elif text == '❔ Ajuda':
        return help_command(update, context)
        
    elif "tiktok.com" in text:
        update.message.reply_text("⏳ Processando seu vídeo...")
        if video_url := download_video(text):
            update.message.reply_video(
                video_url,
                caption="✅ Vídeo baixado com sucesso!\n🔧 Criado por: Wellington",
                reply_markup=get_main_menu()
            )
        else:
            update.message.reply_text(
                "❌ Não consegui baixar este vídeo. Envie outro link válido.",
                reply_markup=get_main_menu()
            )
        return -1

    else:
        update.message.reply_text(
            "Por favor, use os botões abaixo ou envie um link direto do TikTok.",
            reply_markup=get_main_menu()
        )

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ajuda", help_command))
    dp.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        handle_message
    ))

    print("🤖 Bot iniciado!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
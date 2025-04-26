import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import time
import threading
import random
from flask import Flask
from threading import Thread

# Sostituisci con il tuo token
TELEGRAM_TOKEN = '7730394803:AAEXhm2YIHDGPth_9zZQfyUsekZhsQj8xgk'
SPORT_RADAR_API_KEY = 'iqRjDEItZJlerWQ0FaeVsmBWhNPngu06JvUUpbI0'

# Per salvare le partite da monitorare
monitored_matches = {}

logging.basicConfig(level=logging.INFO)

# --- Flask app per tenere sveglio il bot ---
app = Flask('')

@app.route('/')
def home():
    return "Bot attivo!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# --------------------------------------------

# Comando /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Benvenuto! Mandami il nome della partita che vuoi monitorare (es: Napoli - Milan)")

# Quando l'utente scrive una partita
def handle_message(update: Update, context: CallbackContext) -> None:
    match_name = update.message.text.strip()
    chat_id = update.effective_chat.id

    update.message.reply_text(f"Inizio a monitorare: {match_name}")
    monitored_matches[chat_id] = match_name

    # Avvia un nuovo thread per monitorare la partita
    threading.Thread(target=monitor_odds, args=(match_name, chat_id, context), daemon=True).start()

# Funzione che controlla se sono uscite le quote
def monitor_odds(match_name, chat_id, context):
    already_alerted = False
    while True:
        print(f"Controllo le quote per: {match_name}")
        
        odds_info = check_if_odds_available(match_name)

        if odds_info and not already_alerted:
            bookmaker = odds_info['bookmaker']
            odds_1 = odds_info['1']
            odds_x = odds_info['X']
            odds_2 = odds_info['2']

            context.bot.send_message(
                chat_id=chat_id, 
                text=(
                    f"Sono uscite le quote per {match_name}!\n"
                    f"📚 Bookmaker: {bookmaker}\n\n"
                    f"➡️ 1 (Vittoria Casa): {odds_1}\n"
                    f"➡️ X (Pareggio): {odds_x}\n"
                    f"➡️ 2 (Vittoria Ospite): {odds_2}"
                )
            )
            already_alerted = True
            break  # Esce dal ciclo una volta avvisato
        
        time.sleep(60)  # Aspetta 60 secondi

# 🔍 Funzione simulata per verificare se le quote sono disponibili
def check_if_odds_available(match_name):
    if random.choice([False, False, False, True]):  # Simulazione: a volte sono disponibili
        bookmakers = ["Bet365", "Snai", "William Hill", "Unibet", "Goldbet"]
        bookmaker = random.choice(bookmakers)
        odds = {
            'bookmaker': bookmaker,
            '1': round(random.uniform(1.5, 3.0), 2),
            'X': round(random.uniform(2.5, 4.5), 2),
            '2': round(random.uniform(1.8, 3.2), 2),
        }
        return odds
    else:
        return None

# Avvia il bot
if __name__ == '__main__':
    keep_alive()  # Avvia il server Flask per UptimeRobot
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    print("Bot avviato!")
    updater.idle()

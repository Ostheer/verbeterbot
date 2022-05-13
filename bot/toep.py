#!/bin/env python3

# Haal gedeelde boekerijen binnen
import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, Dispatcher, MessageHandler, Filters
import json
import afhandelaars

# Onveranderlijke voorwerpen
MERKTEKEN = os.getenv("BTL_TELEGRAM_BOT_TOKEN")
VROON = os.getenv("BTL_TELEGRAM_BOT_DOMAIN")
GBO = f"https://{VROON}/{MERKTEKEN}" # Gelijkvormige Bron-Oordsbeschrijving

# Maak de toepassing aan
toep = Flask(__name__)

def hoofdzaak():
    # Maak de dwangwerker en diens verzender aan
    dwangwerker = Bot(MERKTEKEN)
    verzender = Dispatcher(dwangwerker, None, workers=8, use_context=True)

    # Koppel afhandelaars aan de verzender
    verzender.add_handler(CommandHandler("start", afhandelaars.start))
    verzender.add_handler(CommandHandler("ontacht", afhandelaars.ontacht))
    verzender.add_handler(CommandHandler("heracht", afhandelaars.heracht))
    verzender.add_handler(CommandHandler("verbeter", afhandelaars.voeg_toe))
    verzender.add_handler(MessageHandler(Filters.text, afhandelaars.verbeter))

    # Schakel de webhaak in
    dwangwerker.delete_webhook()
    dwangwerker.set_webhook(url=GBO)

    # Bepaal de leiden
    @toep.route('/' + MERKTEKEN, methods=['POST'])
    def webhaak():
        json_string = request.stream.read().decode('utf-8')
        nieuws = Update.de_json(json.loads(json_string), dwangwerker)
        verzender.process_update(nieuws)
        return 'ok', 200

# Voer dit uit wanneer het bestand uitgevoerd word
if __name__ == "__main__":
    hoofdzaak()
    toep.run(host='0.0.0.0', port=80)

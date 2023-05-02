#!/bin/env python3

# Haal gedeelde boekerijen binnen
import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, Application, MessageHandler, filters
import json
import afhandelaars
import asyncio

# Onveranderlijke voorwerpen
MERKTEKEN = os.getenv("BTL_TELEGRAM_BOT_TOKEN")
VROON = os.getenv("BTL_TELEGRAM_BOT_DOMAIN")
GBO = f"https://{VROON}/{MERKTEKEN}" # Gelijkvormige Bron-Oordsbeschrijving

# Maak de toepassing aan
toep = Flask(__name__)

async def hoofdzaak():
    # Maak de dwangwerker en diens toepassing aan
    # dwangwerker = Bot(MERKTEKEN)
    # toepassing = Dispatcher(dwangwerker, None, workers=8, )
    toepassing = Application.builder().token(MERKTEKEN).read_timeout(10e3).build()
    await toepassing.initialize()
    dwangwerker = toepassing.bot

    # Koppel afhandelaars aan de toepassing
    toepassing.add_handler(CommandHandler("start", afhandelaars.start))
    toepassing.add_handler(CommandHandler("ontacht", afhandelaars.ontacht))
    toepassing.add_handler(CommandHandler("heracht", afhandelaars.heracht))
    toepassing.add_handler(CommandHandler("verbeter", afhandelaars.voeg_toe))
    toepassing.add_handler(CommandHandler("verwijs", afhandelaars.verwijs))
    toepassing.add_handler(CommandHandler("verwijder", afhandelaars.verwijder))
    toepassing.add_handler(MessageHandler(filters.TEXT, afhandelaars.verbeter))

    # Schakel de webhaak in
    await dwangwerker.delete_webhook()
    await dwangwerker.set_webhook(url=GBO)

    # Bepaal de leiden
    @toep.route('/' + MERKTEKEN, methods=['POST'])
    async def webhaak():
        json_string = request.stream.read().decode('utf-8')
        nieuws = Update.de_json(json.loads(json_string), dwangwerker)
        await toepassing.process_update(nieuws)
        return 'ok', 200

# Voer dit uit wanneer het bestand uitgevoerd word
if __name__ == "__main__":
    asyncio.run(hoofdzaak())
    toep.run(host='0.0.0.0', port=80)

#!/bin/env python3

import os, asyncio

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from telegram import Update
from telegram.ext import Application, CommandHandler

# Onveranderlijke voorwerpen
MERKTEKEN = os.getenv("BTL_TELEGRAM_BOT_TOKEN")
VROON = os.getenv("BTL_TELEGRAM_BOT_DOMAIN")

async def start(update, _):
    await update.message.reply_text("Doe je ding")


async def main():
    application = Application.builder().token(MERKTEKEN).updater(None).build()

    # register handlers
    application.add_handler(CommandHandler("start", start))

    # Pass webhook settings to telegram
    await application.bot.set_webhook(url=f"https://{VROON}/telegram")

    # Set up webserver
    async def telegram(request: Request):
        await application.update_queue.put(Update.de_json(data=await request.json(), bot=application.bot))
        return Response()

    starlette_app = Starlette(
        routes=[
            Route("/telegram", telegram, methods=["POST"]),
        ]
    )
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=starlette_app,
            port=80,
            use_colors=False,
            host="0.0.0.0",
        )
    )

    # Run application and webserver together
    async with application:
        await application.start()
        await webserver.serve()
        await application.stop()


if __name__ == "__main__":
    asyncio.run(main())

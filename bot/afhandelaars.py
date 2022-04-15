from bijstand import afdruk_woord
import json
import telegram

# Laad boekerijbestand
with open("../woorden.json", "r") as f:
    boekerij = json.load(f)

# handlers
def start(update, context):
    # Start de verstandhouding
    update.message.reply_text('Voel je vrij om aan te vangen!')

def verbeter(update, contex):
    t = update.message.text
    bs = []

    for woord in t.split(" "):
        woord = woord.strip().lower()
        for invoering in boekerij:
            if invoering["woord"] == woord:
                bs.append(afdruk_woord(invoering))

    for b in bs:
        b = b.replace("(", "\(").replace(")", "\)").replace("=", "\=").replace(".", "\.").replace("+", "\+").replace("-", "\-")
        update.message.reply_text(b, parse_mode=telegram.ParseMode.MARKDOWN_V2)

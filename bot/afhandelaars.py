from bijstand import afdruk_woord, vergelijk_woorden
import json
import telegram
import string

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
        
    for invoering in boekerij:
        if vergelijk_woorden(t, invoering["woord"]):
            bs.append(afdruk_woord(invoering))

    for b in bs:
        for tv in "()=.+-": b = b.replace(tv, "\\" + tv)
        update.message.reply_text(b, parse_mode=telegram.ParseMode.MARKDOWN_V2)

from bijstand import afdruk_woord
import json

# Laad boekerijbestand
with open("../woorden.json", "r") as f:
    boekerij = json.load(f)

# handlers
def start(update, context):
    # Start de verstandhouding
    update.message.reply_text('Voel je vrij om aan te vangen!')

def verbeter(update, contex):
    t = update.message.text
    b = ""

    for woord in t.split(" "):
        woord = woord.strip().lower()
        if woord in boekerij:
            b += afdruk_woord(woord, boekerij[woord])

    if b:
        update.message.reply_text(b)

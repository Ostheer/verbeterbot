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
        if vergelijk_woorden(t, invoering["woord"], "ww." in invoering["grammatica"] if "grammatica" in invoering else False):
            bs.append(invoering)
    
    bbs = []
    for b in bs:
        if not any(b["woord"] in bb["woord"] and not b == bb for bb in bs):
            bbs.append(afdruk_woord(b))
    

    for b in bbs:
        for tv in "()=.+-[]": b = b.replace(tv, "\\" + tv)
        update.message.reply_text(b, parse_mode=telegram.ParseMode.MARKDOWN_V2)

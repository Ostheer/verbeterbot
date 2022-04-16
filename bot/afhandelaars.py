from bijstand import afdruk_woord, vergelijk_woorden
import json
import telegram
import string

# Laad boekerijbestand
with open("../woorden.json", "r") as f:
    boekerij = json.load(f)

with open("../ontacht.json", "r") as f:
    ontacht = json.load(f)

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
    
    for invoering in ontacht:
        if vergelijk_woorden(t, invoering["woord"], "ww." in invoering["grammatica"] if "grammatica" in invoering else False):
            bs.append(invoering)
    
    bbs = []
    for b in bs:
        #dit haalt woorden eruit als die volledig omvat worden door een ander boekerijwoord. bv. bar valt weg indien barbecue ook is gevonden.
        #TODO: eigenlijk moet dit per woord gebeuren
        if not any(b["woord"] in bb["woord"] and not b == bb for bb in bs):
            if "betekenissen" in b: #indien het geen beteknissen heeft, is deze b er eentje om te ontachten
                bbs.append(afdruk_woord(b))
    

    for b in bbs:
        for tv in "()=.+-[]": b = b.replace(tv, "\\" + tv)
        update.message.reply_text(b, parse_mode=telegram.ParseMode.MARKDOWN_V2)

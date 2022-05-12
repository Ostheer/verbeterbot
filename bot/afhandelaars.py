from bijstand import afdruk_woord, vergelijk_woorden
import json
import telegram
import string

# Laad boekerijbestand
with open("../woorden.json", "r") as f:
    BOEKERIJ = json.load(f)

with open("../ontacht.json", "r") as f:
    ONTACHT = json.load(f)

def schrijf_weg(gegevens):
    if gegevens == "ontacht":
        veranderlijke = ONTACHT
        bestand = "../ontacht.json"
    elif gegevens == "boekerij":
        veranderlijke = BOEKERIJ
        bestand = "../boekerij.json"
    else:
        raise ValueError("Gegevenssoort niet bekend")

    with open(bestand, "w") as bestand:
        json.dump(veranderlijke, bestand)


# handlers
def start(update, context):
    # Start de verstandhouding
    update.message.reply_text('Voel je vrij om aan te vangen!')

def verbeter(update, contex):
    t = update.message.text
    bs = []
        
    for invoering in BOEKERIJ:
        if vergelijk_woorden(t, invoering["woord"], "ww." in invoering["grammatica"] if "grammatica" in invoering else False):
            bs.append(invoering)
    
    for invoering in ONTACHT:
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

def ontacht(update, context):
    # Ontacht vanaf nu een woord
    _, *dingen = update.message.text.split(" ")
    
    if not dingen:
        update.message.reply_text("Momenteel ziet de bond de volgende woorden door de vingers:\n" + ", ".join([o["woord"].capitalize() for o in ONTACHT]))
        return
    else:
        te_ontachten, *verder = dingen

    if any(o["woord"] == te_ontachten.lower() for o in ONTACHT):
        update.message.reply_text("We ontachten dit woord reeds.")
        return

    o = dict(woord=te_ontachten.lower())

    if len(verder) == 0:
        pass
    elif len(verder) == 1:
        woordsoort = verder[0]

        if woordsoort.lower() in ("werkwoord", "ww"):
            o.update(grammatica = "ww.")
        else:
            update.message.reply_text("Onbekende woordsoort")
            return
    else:
        update.message.reply_text("Te veel waarden!")
        return
    
    ONTACHT.append(o)

    update.message.reply_text(f"De bond gedoogt '{te_ontachten}' voortaan.")

    schrijf_weg("ontacht")

def heracht(update, context):
    try:
        _, te_herachten = update.message.text.split(" ")
    except ValueError:
        update.message.reply_text("Onjuiste invoer. Gebruikswijze: '/heracht te_herachten_woord'.")
        return

    for i, o in enumerate(ONTACHT):
        if o["woord"] == te_herachten.lower():
            del ONTACHT[i]
            schrijf_weg("ontacht")
            update.message.reply_text(f"{te_herachten.capitalize()} zal weer verbeterd worden.")
            break
    else:
        update.message.reply_text("Dit woord wordt niet ontacht.")


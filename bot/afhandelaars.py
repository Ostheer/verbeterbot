from bijstand import afdruk_woord, vergelijk_woorden, ontsnap_karakters
from aantekenaars import aantekenaar
import json, telegram, string, shlex

# Laad boekerijbestand
with open("../woorden.json", "r") as f:
    BOEKERIJ = json.load(f)

with open("../ontacht.json", "r") as f:
    ONTACHT = json.load(f)

beheerders = (65607986, 482780937, 63650208)

def bevoegd(update):
    if not update.effective_user["id"] in beheerders:
        update.message.reply_text("Onbevoegd")
        return False
    else:
        return True

def schrijf_weg(gegevens):
    if gegevens == "ontacht":
        veranderlijke = ONTACHT
        bestand = "../ontacht.json"
    elif gegevens == "boekerij":
        veranderlijke = BOEKERIJ
        bestand = "../woorden.json"
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
        if metriek := vergelijk_woorden(t, invoering["woord"], "ww." in invoering["grammatica"] if "grammatica" in invoering else False):
            bs.append((invoering, metriek))

    for invoering in ONTACHT:
        if metriek := vergelijk_woorden(t, invoering["woord"], "ww." in invoering["grammatica"] if "grammatica" in invoering else False):
            bs.append((invoering, metriek))    

    bbs = []
    for b, metriek in bs:
        #dit haalt woorden eruit als die volledig omvat worden door een ander boekerijwoord. bv. bar valt weg indien barbecue ook is gevonden.
        #TODO: eigenlijk moet dit per woord gebeuren
        is_omvat = False
        is_hoger = False
        is_lager = False
        for b2, metriek2 in bs:
            if b2 == b:
                continue
            if metriek > metriek2:
                is_hoger = True
            if metriek < metriek2:
                is_lager = True
            if b["woord"] in b2["woord"]:
                is_omvat = True
       
        if is_lager:
            continue
        if is_omvat and not is_hoger:
            continue
        if not "betekenissen" in b:
            continue

        bbs.append(afdruk_woord(b))
        aantekenaar.info(b["woord"] + ", " + str(update.effective_user))


    for b in bbs:
        update.message.reply_text(ontsnap_karakters(b), parse_mode=telegram.ParseMode.MARKDOWN_V2)

def ontacht(update, context):
    if not bevoegd(update):
        return

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
    if not bevoegd(update):
        return

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

ondersteunde_sleutels = ("grammatica", "herkomst", "verwijzing", "vervang")
def voeg_toe(update, context):
    if not bevoegd(update):
        return
    
    _, woord, betekenissen, *sswvern = shlex.split(update.message.text)
    swvern = dict() #sleutelwoordveranderlijken
    for sw in sswvern:
        sleutel, waarde = sw.split("=", 1)
        swvern[sleutel.lower()] = waarde
    
    betekenissen = [b.strip() for b in betekenissen.split(",")]

    for i, betekenis in enumerate(betekenissen):
        betekenissen[i] = betekenis.replace(">>", "»")
    
    
    for sleutel, waarde in swvern.items():
        if sleutel not in ondersteunde_sleutels:
            update.message.reply_text(f"Onbekend sleutelwoord '{sleutel}'. Ondersteunde sleutelwoorden: {', '.join(ondersteunde_sleutels)}.")
            return
    
    swvern.update(betekenissen = betekenissen)
    swvern.update(woord = woord)

    vervang = (False if not "vervang" in swvern else swvern["vervang"].lower() == "ja")
    try:
        del swvern["vervang"]
    except KeyError:
        pass

    for i, b in enumerate(BOEKERIJ):
        if b["woord"] == woord:
            if not vervang:
                b = "Woord staat al in de boekerij! Vervangen? Voeg dan 'vervang=ja' toe aan je verzoek.\n\n" + afdruk_woord(b)
                update.message.reply_text(ontsnap_karakters(b), parse_mode=telegram.ParseMode.MARKDOWN_V2)
                return
            else:
                BOEKERIJ[i] = swvern
                b = "Woord vervangen!\n\n" + afdruk_woord(swvern) + "\n\nOude vermelding:\n\n" + afdruk_woord(b)
                update.message.reply_text(ontsnap_karakters(b), parse_mode=telegram.ParseMode.MARKDOWN_V2)
                break
    else:
        b = "Woord toegevoegd!\n\n" + afdruk_woord(swvern)
        update.message.reply_text(ontsnap_karakters(b), parse_mode=telegram.ParseMode.MARKDOWN_V2)
        BOEKERIJ.append(swvern)

    
    schrijf_weg("boekerij")


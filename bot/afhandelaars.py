from bijstand import afdruk_woord, vergelijk_woorden, ontsnap_karakters
from aantekenaars import aantekenaar
import json, telegram, string, shlex
from telegram.ext import ContextTypes

markdown = telegram.constants.ParseMode.MARKDOWN_V2

# Laad boekerijbestand
with open("../woorden.json", "r") as f:
    BOEKERIJ = json.load(f)

with open("../ontacht.json", "r") as f:
    ONTACHT = json.load(f)

beheerders = (65607986, 482780937, 63650208, 15589991)

async def bevoegd(update):
    if not update.effective_user["id"] in beheerders:
        await update.message.reply_text("Onbevoegd")
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
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    # Start de verstandhouding
    await update.message.reply_text('Voel je vrij om aan te vangen!')

async def verbeter(update, contex):
    t = update.message.text
    bs = []

    def dingen(invoering):
        enkel_geheel = invoering["enkel_geheel"] if "enkel_geheel" in invoering else False
        is_ww = "ww." in invoering["grammatica"] if "grammatica" in invoering else False
        return enkel_geheel, is_ww

    for invoering in BOEKERIJ:
        enkel_geheel, is_ww = dingen(invoering)
        if x := vergelijk_woorden(t, invoering["woord"], is_ww, enkel_geheel):
            bs.append((invoering, *x))

    for invoering in ONTACHT:
        enkel_geheel, is_ww = dingen(invoering)
        if x := vergelijk_woorden(t, invoering["woord"], is_ww, enkel_geheel):
            metriek, trefwoord = x
            bs.append((invoering, -abs(metriek), trefwoord))

    for b in bs:
        print(b)

    bbs = []
    for b, metriek, trefwoord in bs:
        #dit haalt woorden eruit als die volledig omvat worden door een ander boekerijwoord. bv. bar valt weg indien barbecue ook is gevonden.
        #TODO: eigenlijk moet dit per woord gebeuren
        is_omvat = []
        omvat    = []
        is_hoger = []
        is_lager = []
        ontacht  = []
        for b2, metriek2, trefwoord2 in bs:
            if b2 == b:
                continue

            is_hoger.append(metriek>metriek2)
            is_lager.append(metriek<metriek2)
            is_omvat.append(b["woord"] in b2["woord"] or trefwoord in b2["woord"])
            omvat.append   (b2["woord"] in b["woord"])
            ontacht.append (b["woord"] == b2["woord"] and metriek2 < 0)
            ontacht[-1] = ontacht[-1] or (b["woord"] in b2["woord"] and metriek2 < 0)

        is_hoger = all(is_hoger)
        is_lager = any(is_lager)
        is_omvat = any(is_omvat)
        omvat    = any(omvat)
        ontacht  = any(ontacht)

        if ontacht:
            pass

        elif omvat and is_lager:
            pass #voorbeeld: bericht = "e-mail". Overeenkomstig met "e-mail" en "e-mailen". "e-mailen" omvat "e-mail" en is een lagere overeenkomst, die verwerpen we dus.

        elif is_omvat and not is_hoger:
            pass # voorbeeld: de overeenkomst "e-mail" bij het bericht "e-mailend". "e-mailen" is dan beter want omvattend, en beide zijn niet geheel.

        elif metriek < 0: #dit is het geval voor te ontachten woorden
            pass

        elif "harde_verwijzing" in b:
            #TODO: woorden die overeenkomen met het verwijswoord en niet met het verwezene moeten weg
            #voorbeeld:
            #bestaande woorden: genoom (mv genomen), nomen
            #verwijzing: genomen -> genoom
            #probleem: nomen komt overeen met genomen, maar dit is een verwijswoord.
            #met enkel "genoom" was nomen niet gevonden. Dit is het gewenste gedrag (denk ik)
            #maar dit is enkel op te lossen door "genomen" er helemaal aan het begin uit te halen?
            #en wat doe enkel_geheel eigenlijk?
            print("verwijzing toegeveogd voor", b)
            verwijzing = b["harde_verwijzing"]
            for invoering in BOEKERIJ:
                if invoering["woord"] == verwijzing:
                    bbs.append(afdruk_woord(invoering))
                    aantekenaar.info("INGREEP_VERWEZEN " + verwijzing + ", " + str(update.effective_user))
                    break

        else:
            print(omvat, is_omvat, is_hoger, "we voegen hem toe, die", b)
            bbs.append(afdruk_woord(b))
            aantekenaar.info("INGREEP " + b["woord"] + ", " + str(update.effective_user))


    bbs_gestuurd = [] #voorkom dubbele vermeldingen
    for b in bbs:
        if b not in bbs_gestuurd:
            await update.message.reply_text(ontsnap_karakters(b), parse_mode=markdown)
            bbs_gestuurd.append(b)

async def ontacht(update, context: ContextTypes.DEFAULT_TYPE):
    if not await bevoegd(update):
        return

    # Ontacht vanaf nu een woord
    _, *dingen = update.message.text.split(" ")

    if not dingen:
        await update.message.reply_text("Momenteel ziet de bond de volgende woorden door de vingers:\n" + ", ".join([o["woord"].capitalize() for o in ONTACHT]))
        return
    else:
        te_ontachten, *verder = dingen

    if any(o["woord"] == te_ontachten.lower() for o in ONTACHT):
        await update.message.reply_text("We ontachten dit woord reeds.")
        return

    o = dict(woord=te_ontachten.lower())

    if len(verder) == 0:
        pass
    elif len(verder) == 1:
        woordsoort = verder[0]

        if woordsoort.lower() in ("werkwoord", "ww"):
            o.update(grammatica = "ww.")
        else:
            await update.message.reply_text("Onbekende woordsoort")
            return
    else:
        await update.message.reply_text("Te veel waarden!")
        return

    ONTACHT.append(o)

    await update.message.reply_text(f"De bond gedoogt '{te_ontachten}' voortaan.")

    aantekenaar.info("ONTACHT " + te_ontachten + ", " + str(update.effective_user))

    schrijf_weg("ontacht")

async def heracht(update, context: ContextTypes.DEFAULT_TYPE):
    if not await bevoegd(update):
        return

    try:
        _, te_herachten = await update.message.text.split(" ")
    except ValueError:
        await update.message.reply_text("Onjuiste invoer. Gebruikswijze: '/heracht te_herachten_woord'.")
        return

    for i, o in enumerate(ONTACHT):
        if o["woord"] == te_herachten.lower():
            del ONTACHT[i]
            schrijf_weg("ontacht")
            await update.message.reply_text(f"{te_herachten.capitalize()} zal weer verbeterd worden.")
            aantekenaar.info("HERACHT " + te_herachten + ", " + str(update.effective_user))
            break
    else:
        await update.message.reply_text("Dit woord wordt niet ontacht.")

ondersteunde_sleutels_voeg_toe = ("grammatica", "herkomst", "verwijzing", "vervang", "enkel_geheel")
async def voeg_toe(update, context: ContextTypes.DEFAULT_TYPE):
    if not await bevoegd(update):
        return

    _, woord, betekenissen, *sswvern = shlex.split(update.message.text)
    swvern = dict() #sleutelwoordveranderlijken
    for sw in sswvern:
        sleutel, waarde = sw.split("=", 1)
        swvern[sleutel.lower()] = waarde

    betekenissen = [b.strip() for b in betekenissen.split(",,")]

    for i, betekenis in enumerate(betekenissen):
        betekenissen[i] = betekenis.replace(">>", "»")


    for sleutel, waarde in swvern.items():
        if sleutel not in ondersteunde_sleutels_voeg_toe:
            await update.message.reply_text(f"Onbekend sleutelwoord '{sleutel}'. Ondersteunde sleutelwoorden: {', '.join(ondersteunde_sleutels_voeg_toe)}.")
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
                await update.message.reply_text(ontsnap_karakters(b), parse_mode=markdown)
                return
            else:
                BOEKERIJ[i] = swvern
                b = "Woord vervangen!\n\n" + afdruk_woord(swvern) + "\n\nOude vermelding:\n\n" + afdruk_woord(b)
                await update.message.reply_text(ontsnap_karakters(b), parse_mode=markdown)
                break
    else:
        b = "Woord toegevoegd!\n\n" + afdruk_woord(swvern)
        await update.message.reply_text(ontsnap_karakters(b), parse_mode=markdown)
        BOEKERIJ.append(swvern)


    aantekenaar.info("VERBETER " + str(swvern) + ", " + str(update.effective_user))
    schrijf_weg("boekerij")

ondersteunde_sleutels_verwijs = ("vervang", "enkel_geheel")
async def verwijs(update, context: ContextTypes.DEFAULT_TYPE):
    if not await bevoegd(update):
        return

    _, woord, verwijzing, *sswvern = shlex.split(update.message.text)
    swvern = dict() #sleutelwoordveranderlijken
    for sw in sswvern:
        sleutel, waarde = sw.split("=", 1)
        swvern[sleutel.lower()] = waarde

    for sleutel, waarde in swvern.items():
        if sleutel not in ondersteunde_sleutels_voeg_toe:
            await update.message.reply_text(f"Onbekend sleutelwoord '{sleutel}'. Ondersteunde sleutelwoorden: {', '.join(ondersteunde_sleutels_verwijs)}.")
            return

    swvern.update(harde_verwijzing = verwijzing)
    swvern.update(woord = woord)

    vervang = (False if not "vervang" in swvern else swvern["vervang"].lower() == "ja")

    try:
        del swvern["vervang"]
    except KeyError:
        pass

    swvern["enkel_geheel"] = (True if not "enkel_geheel" in swvern else swvern["enkel_geheel"].lower() != "nee")

    for i, b in enumerate(BOEKERIJ):
        if b["woord"] == woord:
            if not vervang:
                b = "Woord staat al in de boekerij! Vervangen? Voeg dan 'vervang=ja' toe aan je verzoek.\n\n" + afdruk_woord(b)
                await update.message.reply_text(ontsnap_karakters(b), parse_mode=markdown)
                return
            else:
                BOEKERIJ[i] = swvern
                b = "Woord vervangen!\n\n" + afdruk_woord(swvern) + "\n\nOude vermelding:\n\n" + afdruk_woord(b)
                await update.message.reply_text(ontsnap_karakters(b), parse_mode=markdown)
                break
    else:
        b = "Woord toegevoegd!\n\n" + afdruk_woord(swvern)
        await update.message.reply_text(ontsnap_karakters(b), parse_mode=markdown)
        BOEKERIJ.append(swvern)


    aantekenaar.info("VERWIJS " + str(swvern) + ", " + str(update.effective_user))
    schrijf_weg("boekerij")

async def verwijder(update, context: ContextTypes.DEFAULT_TYPE):
    if not bevoegd(update):
        return

    _, woord = shlex.split(update.message.text)

    for i, b in enumerate(BOEKERIJ):
        if b["woord"] == woord:
            break
    else:
        await update.message.reply_text("De bond kent dit woord niet")
        return

    if "betekenissen" in b:
        betekenissen = ',, '.join(b["betekenissen"])
        ontacht_sleutels = ("betekenissen","woord")
        kwargs = " ".join(f'{sleutel}="{waarde}"' if not sleutel in ontacht_sleutels else "" for sleutel, waarde in b.items())
        hermaak = f'/verbeter {b["woord"]} "{betekenissen}" {kwargs}'
    elif "harde_verwijzing" in b:
        hermaak = f'/verwijs {b["woord"]} {b["harde_verwijzing"]}'
        if "enkel_geheel" in b and not b["enkel_geheel"]:
            hermaak += " enkel_geheel=nee"
    stuur = "Verwijderd. Was dit een dwaling? Voeg het dan opnieuw toe:\n\n" + f"`{hermaak}`"
    await update.message.reply_text(ontsnap_karakters(stuur), parse_mode=markdown)

    aantekenaar.info("VERWIJDER " + woord  + ", " + str(update.effective_user))
    del BOEKERIJ[i]
    schrijf_weg("boekerij")


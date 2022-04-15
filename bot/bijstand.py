

#%%
import unicodedata
import string

def verwijder_nadrukken(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def verwijder_tussentekens(s):
    return s.translate(str.maketrans('', '', string.punctuation))

def vervang_laatste(string, find, replace):
    reversed = string[::-1]
    replaced = reversed.replace(find[::-1], replace[::-1], 1)
    return replaced[::-1]


def afdruk_woord(invoering):
    s = f"• {invoering['woord'].capitalize()}"
    
    try:
        s+= f" (`{invoering['grammatica']}`)"
    except KeyError:
        pass

    try:
        s+= f" (herkomst: _{invoering['herkomst']}_)"
    except KeyError:
        pass

    try:
        s+= f" (anderwaardig: {invoering['toelichting']})"
    except KeyError:
        pass

    s += ":"

    if "betekenissen" in invoering:
        if len(invoering["betekenissen"]) == 1:
            s += f" {invoering['betekenissen']}"
        else:
            s += "\n"
            for i, betekenis in enumerate(invoering['betekenissen']):
                s += f"   *{i+1}.* {betekenis}\n"

    elif "verwijzing" in invoering:
        s += f" De ploeg van Bond Tegen Leenwoorden en SDS-8-014 V.O.F. verwijst u graag door naar {invoering['verwijzing'].strip().capitalize()}"
    
    else:
        s += " De Bond heeft hier een mening over, maar ik kan niet goed uitdrukken wat die precies is."
    
    return s

#%%
voorstukjes = ("ge", "be", "a", "on", "de")

def vergelijk_woorden(gebruiker, boekerij):
    def is_overeenkomstig(gebr, boek):
        #TODO: this boek/poging must be at the end of a word (plural form cannot be succeeded by more characters)
        #TODO: minimum size of boek w.r.t. the word, so that "bar" doesn't match "barbecue"
        if boek in gebr:
            woorden = gebr.split(" ")
            for woord in woorden:

                # woordenboekmelding moet wel in het woord van de gebruiker zitten
                if not boek in woord:
                    continue
                
                # woordenboekmelding mag niet onredelijk klein zijn t.o.v. gebruikerswoord
                if not (len(boek) >= 4 or len(woord) <= 5):
                    continue

                # als het ermee eindigt of begint is het sowieso ok
                if (woord.endswith(boek) or woord.startswith(boek)):
                    return True


                # extra uitsluitingscondities voor meervoudsvormen 
                if meervoudsvormen:
                    voor, *midden, na = woord.split(boek)
                    if midden:
                        continue #woordenboekwoord komt meermaals voor, dat zou niet het geval moeten zijn
                    if (not voor in voorstukjes and len(voor) <= 2) or len(na) <= 2:
                        continue #segmentje voor of na is maar één letter, dat kan nooit een losstaand woord of voorzetselgeval zijn
                    if not any(k in voor + na for k in "euioa"): #er moet een medeklinker in het voor/nastukje zitten
                        continue
                
                return True
                


        
        return False
    
    
    # Ga na of het makkelijk is
    meervoudsvormen = False
    if is_overeenkomstig(gebruiker, boekerij):
        return True
    
    gebruiker = verwijder_nadrukken(verwijder_tussentekens(gebruiker.strip().lower()))
    
    if is_overeenkomstig(gebruiker, boekerij):
        return True
    

    # Ga na of er meervoudsvormen in het spel zijn
    meervoudsvormen = True
    mogelijkheden = []

    # Bijzondere gevallen
    if len(boekerij) > 3: #dergelijke woorden uit het Latijn zijn doorgaans niet zo kort (en anders jammer)
        if boekerij.endswith("um"):
            mogelijkheden.append(boekerij[:-2] + "a")

        elif boekerij.endswith("a"):
            mogelijkheden.append(boekerij + "e")

        elif boekerij.endswith("us"):
            mogelijkheden.append(boekerij[:-2] + "i")

        elif boekerij.endswith("ix"):
            mogelijkheden.append(boekerij[:-1] + "ces")

    # Bespaar moeite als het al gelukt is
    if any(is_overeenkomstig(gebruiker, poging) for poging in mogelijkheden):
        return True
    else:
        mogelijkheden = []

    # Standaardgevallen
    #bot->botten
    if any(boekerij.endswith(l) for l in "bcdfghjklmnpqrstvwxz") and boekerij[-2] in "euioa" and (len(boekerij) < 3 or boekerij[-3] not in "euioa"):
        mogelijkheden.append(boekerij + boekerij[-1] + "en")
    
    #keus->keuzen/keusen
    elif any(boekerij.endswith(l) for l in "bcdfghjklmnpqrstvwxz") and (boekerij[-3:-1] in ("eu", "ui", "oe", "au", "ou")):
        if boekerij.endswith("s"):
            boekerij2 = boekerij[:-1] + "z"
            mogelijkheden.append(boekerij2[:-1] + boekerij2[-1] + "en")

        elif boekerij.endswith("f"): 
            boekerij2 = boekerij[:-1] + "v"
            mogelijkheden.append(boekerij2[:-1] + boekerij2[-1] + "en")
        
        mogelijkheden.append(boekerij + "en")
    
    #kaas->kasen/kazen
    elif any(boekerij.endswith(l) for l in "bcdfghjklmnpqrstvwxz") and (boekerij[-2] in "euioa" and boekerij[-3] == boekerij[-2]):
        if boekerij.endswith("s"):
            boekerij2 = boekerij[:-1] + "z"
            mogelijkheden.append(boekerij2[:-2] + boekerij2[-1] + "en")

        elif boekerij.endswith("f"): 
            boekerij2 = boekerij[:-1] + "v"
            mogelijkheden.append(boekerij2[:-2] + boekerij2[-1] + "en")

        mogelijkheden.append(boekerij[:-2] + boekerij[-1] + "en")

    #actie->acties
    elif any(boekerij.endswith(ll) for ll in ("e", "em", "ie", "er", "el", "en", "y", "o", "u", "a", "i")): #y-i is eigenlijk apostrof-s, maar die zijn al weggehaald
        mogelijkheden.append(boekerij + "s")

    return any(is_overeenkomstig(gebruiker, poging) for poging in mogelijkheden)

# %%

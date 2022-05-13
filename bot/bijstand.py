

#%%
import unicodedata
import string

def verwijder_nadrukken(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def verwijder_tussentekens(s):
    return s.translate(str.maketrans('', '', "!\"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~")) #this is string.punctuation, minus the '-'

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
            s += f" {invoering['betekenissen'][0]}"
        else:
            s += "\n"
            for i, betekenis in enumerate(invoering['betekenissen']):
                s += f"   *{i+1}.* {betekenis}\n"

    elif "verwijzing" in invoering:
        s += f" De ploeg van Bond Tegen Leenwoorden en SDS-8-014 V.O.F. verwijst u graag door naar {invoering['verwijzing'].strip().capitalize()}"
    
    elif "harde_verwijzing" in invoering:
        s += f"Harde verwijzing naar {invoering['harde_verwijzing']}."
        if invoering["enkel_geheel"]:
            s += " Enkel gehele overeenkomsten zullen worden verbeterd."
    else:
        s += " De Bond heeft hier een mening over, maar ik kan niet goed uitdrukken wat die precies is."
    
    return s

def ontsnap_karakters(s):
    for tv in "()=.+-[]!":
        s = s.replace(tv, "\\" + tv)
    
    return s

#%%
voorstukjes = "ge", "be", "a", "on", "de"

def vergelijk_woorden(gebruiker, boekerij, is_werkwoord, enkel_geheel):
    def is_overeenkomstig(gebr, boek):
        if not boek in gebr:
            return False
        
        while "  " in gebr: gebr = gebr.replace("  ", " ")

        woorden = gebr.split(" ")
        for woord in woorden:
            # woordenboekmelding moet wel in het woord van de gebruiker zitten
            if not boek in woord:
                # print(1)
                continue

            # uiteraard
            if woord == boek:
                # print(2)
                return 2
            
            else:
                #door hier "waar" terug te geven, slaan we de onderstaande tests over. Omdat we enkel geïnteresseerd zijn in gehele overeenkomsten, 
                #willen we dat omdat we dan "-1" terug kunnen geven aan de aanroeper van vergelijk_woorden, d.w.z. het woord zal ontacht worden. Jezus deze code wordt echt een ramp
                if enkel_geheel:
                    return True

            # woordenboekmelding mag niet onredelijk klein zijn t.o.v. gebruikerswoord
            if not (len(boek) >= 4 or len(woord) <= 5):
                # print(3)
                continue

            voor, *midden, na = woord.split(boek)

            #woordenboekwoord komt meermaals voor, dat zou niet het geval moeten zijn
            if midden and na:
                # print(4)
                continue 

            #segmentje voor of na is maar één letter, dat kan nooit een losstaand woord of voorzetselgeval zijn
            if voor and (not voor in voorstukjes and len(voor) <= 2) or na and len(na) <= 2:
                # print(5)
                continue 
            
            #er moet een medeklinker in het voor/nastukje zitten
            if not any(k in voor + na for k in "euioa"): 
                # print(6)
                continue
            
            return True
        
        return False
    
    gebruiker = verwijder_nadrukken(verwijder_tussentekens(gebruiker.strip().lower()))
    boekerij = verwijder_nadrukken(boekerij).lower()
    
    # Ga na of het makkelijk is
    if waarde:= is_overeenkomstig(gebruiker, boekerij):
        if enkel_geheel:
            if waarde == 2:
                return 100
            else:
                return -1 #dit zal ontacht worden
        else:
            return 100
    
    mogelijkheden = []
    if not is_werkwoord:
        # Ga na of er meervoudsvormen in het spel zijn

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
        #actie->acties
        if any(boekerij.endswith(ll) for ll in ("e", "em", "ie", "er", "el", "en", "y", "o", "u", "a", "i")) and not (boekerij[-2] in ("aeou") and boekerij[-2] == boekerij[-3]): #y-i is eigenlijk apostrof-s, maar die zijn al weggehaald
            #hetgeen na de "and not" is om ervoor te zorgen dat kool/systeem/etc (herhalende klinkers) hier niet worden behandeld
            mogelijkheden.append(boekerij + "s")

        #bot->botten
        elif any(boekerij.endswith(l) for l in "bcdfghjklmnpqrstvwxz") and boekerij[-2] in "euioa" and (len(boekerij) < 3 or boekerij[-3] not in "euioa"):
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


        return any(is_overeenkomstig(gebruiker, poging) for poging in mogelijkheden)

    else:
        # Werkwoord
        # print(f"{boekerij} is een werkwoord")
        if boekerij.endswith("eren"):
            stam = boekerij[:-4]
            mogelijkheden.extend((stam+"eer", stam+"eert", stam+"eerde", stam+"eerden", stam+"eerd", stam+"eerdt"))
            mogelijkheden.extend((boekerij + "d", boekerij + "den", boekerij + "de"))
            return any(is_overeenkomstig(gebruiker, poging) for poging in mogelijkheden)*100 #hogere metriek, dergelijke werkwoordsvormen zijn betrouwbaarder dan meervoudvormen hierboven
        elif boekerij.endswith("en"):
            stam = boekerij[:-2]
            mogelijkheden.extend((stam+"t", stam+"de", stam+"den", stam+"d", stam+"dt"))
            mogelijkheden.extend((boekerij + "d", boekerij + "den", boekerij + "de"))

            uitgangsvormen = any(is_overeenkomstig(gebruiker, poging) for poging in mogelijkheden)*100 #hogere metriek, dergelijke werkwoordsvormen zijn betrouwbaarder dan meervoudvormen hierboven
            stamvorm = 50*bool(is_overeenkomstig(gebruiker, stam)) #is_overeenkomstig geeft 2 wanneer geheel overeenkomstig, we willen echter 50 punten toekennen en niet 100 indien overeenkomstig
            return max(uitgangsvormen, stamvorm)



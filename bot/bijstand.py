import unicodedata
import string

def verwijder_nadrukken(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def verwijder_tussentekens(s):
    return s.translate(str.maketrans('', '', string.punctuation))

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
        s += f"De ploeg van Bond Tegen Leenwoorden en SDS-8-014 V.O.F. verwijst u graag door naar {invoering['verwijzing']}"
    
    else:
        s += "De Bond heeft hier een mening over, maar ik kan niet goed uitdrukken wat precies."
    
    return s

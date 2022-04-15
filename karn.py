#!/bin/env python3

#%%
import json

with open("lijst.txt", "r") as f:
    regels = f.readlines()


def splijt_op_plaatsgetal(s, i):
    return s[:i], s[i+1:]

#%%
boekerij = []
afwijkend = []
for regel in regels:
    if not regel.strip():
        continue
    
    if regel.count("[") != regel.count("]") or regel.count("(") != regel.count(")"):
        afwijkend.append(regel)
        continue
    
    invoering = dict()

    # Karn de regel tot een invoering
    stronk = ""
    for i, ss in enumerate(regel):
        if ss.lower() not in "()[],.;»<>":
            stronk += ss
        else:
            invoering["woord"] = stronk.strip()
            rest = regel[i:].strip()
            break

    
    if rest.startswith("<"):
        invoering["toelichting"], rest = rest[1:].split(">",1)
        rest = rest.strip()

    if rest.startswith("("):
        invoering["grammatica"], rest = rest[1:].split(")",1)
        rest = rest.strip()

    #vrouwelijke vorm is vernoemd, misschien
    if rest.startswith(", "):
        sla_over = False
        rest_kopij = rest

        try:
            vvorm, rest = rest.split(", ", 1)[1].split(" ", 1)
            if vvorm.strip() == "1":
                # begin definitie van betekenis, dus geen vrouwelijke vorm
                rest = rest_kopij
                raise ValueError
        except ValueError:
            # Gebeurt wanneer geen vierkante haken en maar één betekenis. voorbeeld:
            #bohémien (attributief bn.), Boheems.
            sla_over = True
        
        if not sla_over:
            if rest.startswith("("):
                invoering["vrouwelijk"] = vvorm
                invoering["grammatica vrouwelijk"], rest = rest[1:].split(")",1)
                rest = rest.strip()
            else:
                rest = rest_kopij


    if rest.startswith("["):
        invoering["herkomst"], rest = rest[1:].split("]",1)
        rest = rest.strip()
    
    if rest.startswith(", zie"):
        invoering["verwijzing"] = rest.split(", zie")[1]

    else:
        #oude aanpak: rest = rest.replace(".;", "---HOERENKOTSHOERENKOTSHOERENKOTS---") #vervang tijdelijk, zodat ";" voorafgegaan door "." (zoals voorkomende in grammaticatoelichtingen) niet gezien worden als betekenisscheiding
        #maar niet al zulke ; worden door . voorafgegaan. Splijt daarom als volgt (wanneer ; temidden van oneven aantal open- en sluithaken):
        vervang = []
        for i, r in enumerate(rest):
            if r == ";":
                if rest[i:].count(")")!=rest[i:].count("(") and rest[:i].count("(")!=rest[:i].count(")"):
                    print(rest[i:])
                    print(rest[:i])
                    vervang.append(i)
        for i in vervang[::-1]: #vervang omgekeerd zodat plaatsgetallen gelijk blijven
            print("vervang", i)
            rest = "---HOERENKOTSHOERENKOTSHOERENKOTS---".join(splijt_op_plaatsgetal(rest, i))

        #karn eindelijk de betekenissen
        betkns = rest.strip(",. \n\t").split("; ")
        for i, b in enumerate(betkns):
            b = b.replace("---HOERENKOTSHOERENKOTSHOERENKOTS---", ";")
            b = b.strip(",. \n\t")
            while b[0] in "1234567890":
                b = b[1:]
            b = b.strip(",. \n\t")
            betkns[i] = b

        invoering["betekenissen"] = betkns
    
    try:
        if not invoering["betekenissen"]:
            print(invoering)
            print(regel)
            raise ValueError("GEEN BETEKENISSEN")
    except KeyError:
        pass
        

    
    boekerij.append(invoering)


#%%
with open("woorden.json", "w") as f:
    f.write(json.dumps(boekerij))
# %%

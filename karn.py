#!/bin/env python3

import json

with open("woorden.txt", "r") as f:
    regels = f.readlines()

sch = ";"
hrk = "»"
ops = ","

w = dict()

for regel in regels:
    woord, *betkn = regel.split(sch)
    w[woord] = []
    for betk in betkn:
        if hrk in betk:
            uitleg, betekenissen = betk.split(hrk)
        else:
            uitleg = None
            betekenissen = betk
        
        betekenissen = betekenissen.split(ops)
        betekenissen = [b.strip().lower() for b in betekenissen]

        w[woord].append([uitleg, betekenissen])


with open("woorden.json", "w") as f:
    f.write(json.dumps(w))

#!/bin/env python3

#herkarn een uitvoer naar een boekerij
import json

# Laad uitvoer
with open("../uitvoer.json", "r") as f:
    uitvoer = json.load(f)

boekerij = dict()

for invoering in uitvoer:
    betekenissen = []
    for betekenis in invoering["betekenissen"]:
        betekenissen.append()
    boekerij[invoering["woord"]] = betekenissen
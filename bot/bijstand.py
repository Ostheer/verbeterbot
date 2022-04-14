def afdruk_woord(woord, inhoud):
    def maak(betekenissen, uitleg):
        return f"{f'{uitleg} --> ' if uitleg else ''}{', '.join([b.capitalize() for b in betekenissen])}"
    
    s = ""

    if len(inhoud) == 1:
        uitleg, betekenissen = inhoud[0]
        s += f"* {woord.capitalize()}: {maak(betekenissen, uitleg)}\n"

    else:
        s += f"* {woord.capitalize()}\n"
        for i, (uitleg, betekenissen) in enumerate(inhoud):
            s += f"\t{i+1}: {maak(betekenissen, uitleg)}\n"

    return s

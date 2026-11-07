#!/usr/bin/env python3
"""Legger inn oppdater-knappen (verktoy/oppdater.js) nederst i alle simulatorene og oversikten.

Når en side er endret på nettet, kommer «Ny versjon av siden er klar. Oppdater» nederst,
som i Verkstedhåndboka. Kjøres også av tema.py. Kan kjøres flere ganger:
    python3 verktoy/oppdater.py
"""
import pathlib
import re

ROT = pathlib.Path(__file__).resolve().parent.parent
START, SLUTT = "<!--lk:oppdater-->", "<!--lk:oppdater-slutt-->"


def legg_inn():
    js = (ROT / "verktoy" / "oppdater.js").read_text(encoding="utf-8")
    blokk = f"{START}<script>\n{js}</script>{SLUTT}"
    for sti in sorted(ROT.glob("*.html")):
        s = re.sub(re.escape(START) + ".*?" + re.escape(SLUTT), "", sti.read_text(encoding="utf-8"), flags=re.S)
        k = s.rfind("</body>")
        s = s[:k] + blokk + s[k:] if k > 0 else s + blokk
        sti.write_text(s, encoding="utf-8")


if __name__ == "__main__":
    legg_inn()
    print("ok")

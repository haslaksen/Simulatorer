#!/usr/bin/env python3
"""Gir simulatorene samme form og utseende som leksjonene.

Skriptet legger inn (eller oppdaterer) en felles blokk i hver simulator:
  - toppstripe som i leksjonene: navn, snarveier, A+ (større tekst) og lys/mørk
  - introduksjon i leksjonsstil: emne, tittel, kort ingress og «Slik gjør du» i 3–4 steg
  - leksjonenes farger og skrift (simulatorens egne fargevariabler pekes til leksjonens)

Kjør fra roten av repoet:   python3 verktoy/tema.py
Skriptet kan kjøres flere ganger. Ny simulator: legg HTML-filen i roten og legg til en
oppføring i SIMULATORER nedenfor.
"""
import html
import pathlib
import re
import sys

ROT = pathlib.Path(__file__).resolve().parent.parent
HB = "https://verkstedhandboka.vercel.app/#"

# Leksjonenes fargepalett (samme verdier som i leksjonene)
LYS = dict(bg="#f5f7fa", panel="#ffffff", ink="#14181d", muted="#56606c", line="#d9dfe6",
           blue="#1c6fd1", blue_soft="#e4eefc", orange="#e8590c", orange_soft="#fff0e5",
           green="#2b8a3e", green_soft="#e7f5ea", red="#c92a2a", red_soft="#fdeaea",
           steel_soft="#eceff3", on_accent="#ffffff")
MORK = dict(bg="#12161b", panel="#1b2128", ink="#eef1f5", muted="#a3adb9", line="#2f3843",
            blue="#5aa2f5", blue_soft="#1b2c42", orange="#ff8a3d", orange_soft="#3a2516",
            green="#51cf66", green_soft="#183020", red="#ff6b6b", red_soft="#3a1c1c",
            steel_soft="#262e37", on_accent="#ffffff")

# Felles kobling fra simulatorenes variabelnavn til leksjonens
VERKSTED = {"--bg": "bg", "--panel": "panel", "--ink": "ink", "--muted": "muted", "--line": "line",
            "--accent": "orange", "--accent-ink": "on_accent", "--ok": "green", "--bad": "red",
            "--bench": "steel_soft", "--bench-line": "line",
            "--display": "font", "--body": "font", "--mono": "mono"}
F_VARS = {"--f-display": "font", "--f-body": "font", "--f-mono": "mono"}

SIMULATORER = [
    dict(fil="skyvelaere.html", navn="Skyvelære", emne="Måleteknikk",
         ingress="Les av en skyvelære med nonius. Start med 0,1 mm nonius. Når du får det til, prøver du 0,05 og 0,02.",
         steg=["Les hele millimeter på hovedskalaen, til venstre for nullstreken på noniusen.",
               "Finn den ene noniusstreken som står i flukt med en strek på hovedskalaen. Bruk lupen.",
               "Gang nummeret på streken med oppløsningen, og legg det til.",
               "Skriv svaret og trykk <b>Sjekk</b>."],
         rot="main.wrap", skjul=[".wrap > header"],
         farger={"--bg": "bg", "--panel": "panel", "--fg": "ink", "--muted": "muted", "--line": "line",
                 "--accent": "orange", "--accent-ink": "on_accent", "--ok": "green", "--bad": "red",
                 "--chip": "steel_soft", "--lens": "orange",
                 "--display": "font", "--body": "font", "--mono": "mono"},
         endringer=[("const S={mode:'practice',res:2,", "const S={mode:'practice',res:10,"),
                    ('data-res="10" aria-pressed="false"', 'data-res="10" aria-pressed="true"'),
                    ('data-res="2" aria-pressed="true"', 'data-res="2" aria-pressed="false"')],
         ekstra_css='svg .lbl,svg .vlbl{font-family:"Barlow Condensed","Arial Narrow",sans-serif}'),
    dict(fil="mikrometer.html", navn="Mikrometer", emne="Måleteknikk",
         ingress="Les av et utvendig mikrometer. Hver strek på trommelen er 0,01 mm.",
         steg=["Les hele millimeter på den øvre skalaen på hylsen.",
               "Ser du en strek på den nedre skalaen etter den? Legg til 0,50 mm.",
               "Les trommelstreken som står på linje med lengdestreken. Hver strek er 0,01 mm.",
               "Legg sammen. Øv i <b>Les av</b> og <b>Still inn</b>."],
         rot=".wrap", skjul=[".wrap > header > div:first-child"], farger=VERKSTED),
    dict(fil="maleur.html", navn="Måleur", emne="Måleteknikk",
         ingress="Les av en indikatorklokke, og mål kast og planhet. Hver strek på skiva er 0,01 mm.",
         steg=["Den lille viseren teller hele millimeter.",
               "Den store viseren viser hundredeler: hver strek er 0,01 mm.",
               "Legg sammen: 3 og 47 gir 3,47 mm.",
               "Kast og planhet: nullstill skiva, mål, og regn største minus minste utslag."],
         rot=".wrap", skjul=[".wrap > header > div:first-child"], farger=VERKSTED),
    dict(fil="toleranser.html", navn="Toleranser og pasninger", emne="Måleteknikk",
         ingress="Finn største og minste tillatte mål for hull og aksel, og se om en målt del blir godkjent.",
         steg=["Velg hull eller aksel, og skriv inn nominelt mål.",
               "Velg toleransebokstav og toleransegrad, for eksempel H7.",
               "Les største og minste tillatte mål.",
               "Skriv inn det målte målet, og se om delen blir godkjent."],
         hb=("t2-tol", "2.2 ISO-toleranser"),
         rot=".wrap", skjul=[".wrap > header > div:first-child"], farger=VERKSTED),
    dict(fil="gjenger.html", navn="Gjenger", emne="Måleteknikk",
         ingress="Finn ut hvilken gjenge du har: mål diameteren, finn stigningen og slå opp i tabellen.",
         steg=["Mål ytre diameter med skyvelæra.",
               "Bytt blad i stigningslæra til det ikke er lys mellom bladet og gjengen.",
               "Slå opp diameter og stigning i gjengetabellen.",
               "Prøv <b>Identifiser</b> og <b>Kjernebor</b>. Kjernebor for metrisk gjenge: d − P."],
         hb=("g6-metrisk", "6.1 Metriske gjenger"),
         rot=".wrap", skjul=[".wrap > header > div:first-child"], farger=VERKSTED),
    dict(fil="momentnokkel.html", navn="Momentnøkkel", emne="Montering",
         ingress="Finn riktig tiltrekkingsmoment, still inn momentnøkkelen og trekk til skruen.",
         steg=["Finn momentet i tabellen: dimensjon, fasthetsklasse og om gjengene er smurt.",
               "Lås opp håndtaket og still inn nøkkelen. Lås håndtaket igjen.",
               "Hold inne <b>Hold inne for å trekke</b>, og slipp når nøkkelen klikker.",
               "Sett nøkkelen tilbake til laveste verdi når du er ferdig."],
         hb=("e5-moment", "5.2 Tiltrekkingsmoment"),
         rot=".wrap", skjul=[".wrap > header > div:first-child"], farger=VERKSTED),
    dict(fil="multimeter.html", navn="Multimeter", emne="Elektro",
         ingress="Mål spenning, strøm og motstand med et digitalt multimeter. Velg riktig funksjon, område og kontakt.",
         steg=["Svart ledning i <b>COM</b>. Rød ledning i <b>VΩmA</b> (eller <b>10A</b> for store strømmer).",
               "Velg funksjon: DCV, ACV, Ω eller DCA.",
               "Start på et høyt område, og skru ned til du får flest mulig sifre.",
               "Spenning måles parallelt, over komponenten. Strøm måles i serie."],
         hb=("el9-maling", "9.15 Måling med multimeter"),
         rot=".wrap", skjul=[".wrap > header > div:first-child"], farger=VERKSTED),
    dict(fil="tangamperemeter.html", navn="Tangamperemeter", emne="Elektro",
         ingress="Mål strøm uten å bryte kretsen. Legg tanga rundt én leder, og se hvorfor den viser 0 rundt hele kabelen.",
         steg=["Velg <b>A~</b> på bryteren. Vet du ikke hvor stor strømmen er, start på <b>400 A</b>.",
               "Legg tanga rundt <b>én</b> leder.",
               "Viser displayet <b>OL</b>, velg et høyere område. Få sifre? Velg et lavere.",
               "Prøv tanga rundt hele kabelen. Den viser 0, fordi strømmen fram og tilbake opphever hverandre."],
         hb=("el9-maling", "9.15 Måling med multimeter"),
         rot=".wrap", skjul=[".wrap > header > div:first-child"], farger=VERKSTED),
    dict(fil="biomekanikk.html", navn="Biomekanikk", emne="Treningslære", trinn="Vg3 Idrett",
         ingress="Sju små simulatorer om krefter og bevegelse: knebøy, balanse, kraft og motkraft, vektstang, kast, bevegelseskjeden og landing.",
         steg=["Velg en fane øverst, for eksempel <b>Knebøy</b> eller <b>Balanse</b>.",
               "Dra i gliderne, og se hva som skjer med figuren.",
               "Les av tallene og meldingen til høyre.",
               "Svar på spørsmålene under <b>Prøv dette</b>."],
         rot=".wrap", skjul=[".wrap > header > div:first-child"], farger=VERKSTED),
    dict(fil="skjaeredata.html", navn="Skjæredata", emne="Maskinering",
         ingress="Velg turtall og mating for dreiing og fresing ut fra materiale, verktøy og diameter.",
         steg=["Velg materiale og verktøy.",
               "Finn skjærehastigheten v<sub>c</sub> i tabellen nederst.",
               "Regn ut turtallet: n = v<sub>c</sub> · 1000 / (π · D).",
               "Still inn turtall og mating, og se resultatet. Prøv deretter <b>Oppgave</b>."],
         hb=("m3-valg", "3.1 Valg av skjæredata"),
         rot=".wrap", skjul=[".wrap > header > div:first-child"], farger=VERKSTED),
    dict(fil="cnc-dreiebenk.html", navn="CNC-dreiebenk", emne="Maskinering · CNC",
         ingress="Øv på betjeningspanelet til en Mazak QT Nexus 250. Oppgavene står på skjermen til venstre.",
         steg=["Slipp nødstoppen og trykk <b>RESET</b>.",
               "Velg <b>HOME</b> og nullpunktkjør X og Z.",
               "Velg <b>MDI</b>, skriv G97 S800 M3, lukk døren og trykk <b>CYCLE START</b>.",
               "Følg resten av oppgavene på skjermen."],
         hb=("m3-cnc", "3.15 CNC-koder"),
         rot=".wrap", skjul=[], farger={}, ekstra_css="html,body{background:var(--lk-bg)!important}"),
    dict(fil="cnc-koordinater.html", navn="CNC-koordinater", emne="Maskinering · CNC",
         ingress="Øv på koordinatsystemet. Skriv inn X og Z på dreiebenken, eller X, Y og Z på fresen, og se verktøyet flytte seg dit.",
         steg=["Velg <b>Dreiebenk</b> eller <b>Fres</b>.",
               "Finn punktet i figuren. Nullpunktet heter <b>W</b>. Hver rute er 10 mm.",
               "Skriv inn koordinatene og trykk <b>Flytt</b>. På dreiebenken er X <b>diameteren</b>.",
               "Inn i materialet er Z <b>minus</b>. Treffer du materialet, blir verktøyet rødt."],
         hb=("m3-cnc", "3.15 CNC-koder"),
         rot=".wrap", skjul=[".wrap > header > div:first-child"], farger=VERKSTED),
    dict(fil="strekkprove.html", navn="Strekkprøve", emne="Materiallære",
         ingress="Dra en prøvestav til den ryker, og se hvordan spenning–tøyningskurven bygger seg opp.",
         steg=["Velg et materiale.",
               "Trykk <b>Start</b> og se kurven bygge seg opp.",
               "Les flytegrense, strekkfasthet R<sub>m</sub> og bruddforlengelse A i prøveloggen.",
               "Kjør flere materialer og sammenlign kurvene."],
         hb=("materialer", "Emne 7 Materialer"),
         rot=".wrap", skjul=[".wrap > header > div:first-child"],
         farger={"--bg": "bg", "--panel": "panel", "--ink": "ink", "--muted": "muted", "--line": "line",
                 "--accent": "orange", "--accent-soft": "orange_soft", "--accent-ink": "orange", **F_VARS},
         ekstra_css="body{padding:0!important}.wrap{padding:20px 16px 40px}"),
    dict(fil="charpy.html", navn="Charpy-prøve", emne="Materiallære",
         ingress="Test hvor mye energi et materiale tåler før det brekker ved et brått slag, og se hvordan kulde gjør stål sprøtt.",
         steg=["Velg materiale.",
               "Velg prøvetemperatur.",
               "Trykk <b>Slipp pendelen</b> og les slagenergien KV2.",
               "Prøv flere temperaturer. Når blir stålet sprøtt?"],
         hb=("materialer", "Emne 7 Materialer"),
         rot=".wrap", skjul=[".wrap > header"],
         farger={"--bg": "bg", "--surface": "panel", "--ink": "ink", "--muted": "muted", "--line": "line",
                 "--accent": "orange", "--accent-ink": "on_accent", "--ok": "green", "--bad": "red", **F_VARS}),
    dict(fil="bjelke.html", navn="Bjelke", emne="Mekanikk",
         ingress="Se hvor mye en bjelke bøyer seg, og om den holder. Endre inspenning, profil, lengde og last.",
         steg=["Velg inspenning.",
               "Velg profil og materiale.",
               "Still inn lengde og last.",
               "Se nedbøyning og utnyttelse. Under 100 % betyr at bjelken holder."],
         hb=("me12-nedboy", "12.10 Dragere – nedbøyning"),
         rot=".wrap", skjul=[".wrap > header"],
         farger={"--paper": "bg", "--sheet": "panel", "--ink": "ink", "--muted": "muted", "--rule": "line",
                 "--accent": "orange", "--ok": "green", "--bad": "red", **F_VARS}),
    dict(fil="pneumatikk-og-hydraulikk.html", navn="Pneumatikk og hydraulikk", emne="Pneumatikk",
         ingress="Koble ventiler og sylindre med slanger, og se hva som skjer. Symbolene følger ISO 1219.",
         steg=["Velg en oppgave.",
               "Dra komponentene du trenger inn på koblingsbrettet.",
               "Koble slanger: klikk på en port, og så på porten slangen skal til.",
               "Trykk på knappen eller hendelen, og se sylinderen gå."],
         hb=("h8-symboler", "8.2 Symboler"),
         rot=".wrap", skjul=[".wrap > header > div:first-child"],
         farger={k: v for k, v in VERKSTED.items() if not k.startswith("--bench")}),
    dict(fil="robotlab.html", navn="Robotlab", emne="Automasjon · logikk og styring",
         ingress="Programmer en robot med blokker, og se hva den gjør. Blokkene blir til Arduino-kode.",
         steg=["Velg et oppdrag i menyen.",
               "Bygg programmet med blokker.",
               "Trykk <b>Last opp og kjør</b>.",
               "Se hva roboten gjør, og rett programmet til det virker."],
         rot=".shell", skjul=[".shell > header .brand"],
         farger={"--bg": "bg", "--surface": "panel", "--ink": "ink", "--muted": "muted", "--line": "line",
                 "--accent": "orange", "--accent-ink": "on_accent", "--accent-soft": "orange_soft", **F_VARS}),
]

FONT = '"Segoe UI", system-ui, -apple-system, Roboto, Arial, sans-serif'
MONO = '"Cascadia Mono", Consolas, "JetBrains Mono", ui-monospace, monospace'


def lk_vars(p):
    return "".join(f"--lk-{k.replace('_', '-')}:{v};" for k, v in p.items())


FELLES_CSS = """
:root{%s--lk-scale:1;--lk-font:%s;--lk-mono:%s}
:root[data-theme="light"]{color-scheme:light}
:root[data-theme="dark"]{%scolor-scheme:dark}
.lk-top{margin:0;max-width:none;width:auto;flex-direction:row;justify-content:flex-start;text-align:left;box-shadow:none;position:sticky;top:0;z-index:1000;background:var(--lk-panel);border-bottom:1px solid var(--lk-line);display:flex;align-items:center;gap:12px;padding:0 16px;height:56px;font-family:var(--lk-font);color:var(--lk-ink);line-height:1.5}
.lk-top .lk-brand{font-weight:700;white-space:nowrap;font-size:15px;color:inherit;text-decoration:none}
.lk-top .lk-brand span{color:var(--lk-orange)}
.lk-top .lk-nav{margin:0;padding:0;background:none;border:0;display:flex;gap:5px;overflow-x:auto;flex:1;scrollbar-width:none}
.lk-top .lk-nav::-webkit-scrollbar{display:none}
.lk-top .lk-nav a{white-space:nowrap;text-decoration:none;color:var(--lk-muted);font-size:13px;padding:5px 11px;border-radius:99px;border:1px solid transparent}
.lk-top .lk-nav a:hover{color:var(--lk-blue);border-color:var(--lk-blue);background:var(--lk-blue-soft)}
.lk-tools{display:flex;gap:5px}
.lk-btn{font:inherit;font-size:12px;cursor:pointer;border:1px solid var(--lk-line);background:var(--lk-panel);color:var(--lk-ink);border-radius:10px;padding:5px 10px}
.lk-btn:hover{border-color:var(--lk-blue)}
.lk-intro{font-family:var(--lk-font);color:var(--lk-ink);padding:28px 16px 12px;line-height:1.5;scroll-margin-top:56px}
.lk-in{max-width:var(--lk-w);margin:0 auto;display:grid;grid-template-columns:1.1fr 1fr;gap:24px;align-items:start}
.lk-kicker{font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--lk-orange);margin-bottom:6px}
.lk-intro h1{font-family:var(--lk-font);font-size:40px;line-height:1.1;font-weight:700;letter-spacing:0;text-transform:none;margin:0 0 12px;color:var(--lk-ink)}
.lk-lead{font-size:18px;color:var(--lk-muted);margin:0;max-width:60ch}
.lk-card{background:var(--lk-panel);border:1px solid var(--lk-line);border-radius:14px;padding:16px 18px}
.lk-card h2{font-family:var(--lk-font);font-size:18px;font-weight:700;letter-spacing:0;text-transform:none;margin:0 0 8px;color:var(--lk-ink)}
.lk-steps{counter-reset:lk;list-style:none;padding:0;margin:0}
.lk-steps li{counter-increment:lk;display:flex;gap:10px;align-items:flex-start;margin:7px 0;font-size:15px;line-height:1.4}
.lk-steps li::before{content:counter(lk);flex:none;width:26px;height:26px;border-radius:50%%;display:grid;place-items:center;font-weight:800;font-size:13px;background:var(--lk-orange);color:#fff}
.lk-hb{display:inline-block;margin-top:10px;font-size:14px;color:var(--lk-blue)}
.lk-rot{zoom:var(--lk-scale);scroll-margin-top:56px}
.lk-intro{zoom:var(--lk-scale)}
@media (max-width:800px){.lk-in{grid-template-columns:1fr}.lk-intro h1{font-size:30px}.lk-top .lk-nav{display:none}}
""" % (lk_vars(LYS), FONT, MONO, lk_vars(MORK))

LK_JS = """(function(){var r=document.documentElement,s=1,b=document.getElementById("lkSize");
var root=document.querySelector(%r);if(root){root.classList.add("lk-rot");if(!root.id)root.id="simulator";}
var a=document.getElementById("lkSimLink");if(a&&root)a.href="#"+root.id;
b.onclick=function(){s=s>=1.3?1:+(s+.15).toFixed(2);r.style.setProperty("--lk-scale",s);b.textContent=s===1?"A+":"A"+Math.round(s*100)+"%%";window.dispatchEvent(new Event("resize"));};
document.getElementById("lkTheme").onclick=function(){r.dataset.theme=r.dataset.theme==="dark"?"light":"dark";window.dispatchEvent(new Event("resize"));};})();"""

START, SLUTT = "<!--lk:start-->", "<!--lk:slutt-->"
HSTART, HSLUTT = "<!--lk:head-->", "<!--lk:head-slutt-->"


def fjern(s):
    s = re.sub(re.escape(HSTART) + ".*?" + re.escape(HSLUTT), "", s, flags=re.S)
    s = re.sub(re.escape(START) + ".*?" + re.escape(SLUTT), "", s, flags=re.S)
    s = re.sub(r"<!--lk:js-->.*?<!--lk:js-slutt-->", "", s, flags=re.S)
    return s


def bygg(c):
    sti = ROT / c["fil"]
    s = fjern(sti.read_text(encoding="utf-8"))
    for gammel, ny in c.get("endringer", []):
        if ny in s:
            continue
        assert s.count(gammel) == 1, (c["fil"], gammel)
        s = s.replace(gammel, ny)

    p = {**LYS}
    kart = "".join(f"{k}:var(--lk-{v.replace('_', '-')});" for k, v in c["farger"].items())
    skjul = ",".join(c["skjul"])
    bredde = re.search(re.escape(c["rot"].split(".")[-1]) + r"\{[^}]*max-width:(\d+px)", s)
    css = FELLES_CSS + f":root{{--lk-w:{bredde.group(1) if bredde else '1200px'}}}\n"
    if kart:
        css += f":root[data-theme]{{{kart}}}\n"
    if skjul:
        css += f"{skjul}{{display:none!important}}\n"
    css += c.get("ekstra_css", "")

    head = (f'{HSTART}<script>document.documentElement.dataset.theme="light";</script>'
            f'<style id="leksjonstema">{css}</style>{HSLUTT}')
    # Stilen må komme etter simulatorens egen stil, så den legges rett før siste </head>
    i = s.rfind("</head>")
    assert i > 0, c["fil"]
    s = s[:i] + head + s[i:]

    hb = ""
    if c.get("hb"):
        anker, tekst = c["hb"]
        hb = f'<a class="lk-hb" href="{HB}{anker}" target="_blank" rel="noopener">Les mer i Verkstedhåndboka: {html.escape(tekst)} ↗</a>'
    steg = "".join(f"<li><span>{t}</span></li>" for t in c["steg"])
    topp = f"""{START}
<div class="lk-top" role="banner">
  <a class="lk-brand" href="index.html">Simulator · <span>{html.escape(c['navn'])}</span></a>
  <nav class="lk-nav"><a href="#lk-intro">Slik gjør du</a><a id="lkSimLink" href="#simulator">Simulator</a><a href="index.html">Alle simulatorer</a></nav>
  <div class="lk-tools"><button class="lk-btn" id="lkSize" type="button" title="Større tekst for fremviser">A+</button><button class="lk-btn" id="lkTheme" type="button" title="Lys/mørk">☾</button></div>
</div>
<section class="lk-intro" id="lk-intro">
  <div class="lk-in">
    <div>
      <div class="lk-kicker">{html.escape(c.get('trinn', 'Vg2 industriteknologi'))} · {html.escape(c['emne'])}</div>
      <h1>{html.escape(c['navn'])}</h1>
      <p class="lk-lead">{html.escape(c['ingress'])}</p>
    </div>
    <div class="lk-card">
      <h2>Slik gjør du</h2>
      <ol class="lk-steps">{steg}</ol>
      {hb}
    </div>
  </div>
</section>
{SLUTT}"""
    # Toppstripen settes inn rett etter siste <body> (noen filer har to)
    m = list(re.finditer(r"<body[^>]*>", s))
    assert m, c["fil"]
    j = m[-1].end()
    s = s[:j] + topp + s[j:]
    k = s.rfind("</body>")
    js = f"<!--lk:js--><script>{LK_JS % c['rot']}</script><!--lk:js-slutt-->"
    s = s[:k] + js + s[k:] if k > 0 else s + js
    if 'lang="nb"' not in s[:300]:
        s = s.replace("<html>", '<html lang="nb">', 1)
    sti.write_text(s, encoding="utf-8")
    print("ok", c["fil"])


if __name__ == "__main__":
    valgt = sys.argv[1:]
    for c in SIMULATORER:
        if not valgt or c["fil"] in valgt:
            bygg(c)

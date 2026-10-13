# Simulatorer

Interaktive simulatorer for Industriteknologi. Hver simulator er én frittstående HTML-fil, og ser ut som leksjonene: samme toppstripe (A+ og lys/mørk), samme farger og skrift, og en kort «Slik gjør du» i fire steg før selve simulatoren.

| Emne | Simulatorer |
|---|---|
| Måleteknikk | `skyvelaere.html` · `mikrometer.html` · `maleur.html` · `toleranser.html` · `gjenger.html` |
| Materiallære og mekanikk | `strekkprove.html` · `charpy.html` · `bjelke.html` |
| Maskinering | `skjaeredata.html` · `cnc-dreiebenk.html` |
| Montering | `momentnokkel.html` |
| Elektro | `multimeter.html` |
| Pneumatikk | `pneumatikk-og-hydraulikk.html` |
| Automasjon | `robotlab.html` |

`index.html` er oversiktssiden.

## Leksjonsstilen

Stilen legges inn av `verktoy/tema.py`. Skriptet setter inn en merket blokk (`<!--lk:...-->`) i hver fil og kan kjøres flere ganger:

```
python3 verktoy/tema.py                 # alle simulatorene
python3 verktoy/tema.py multimeter.html # bare én
```

Tekstene i «Slik gjør du», ingress og lenke til Verkstedhåndboka står i listen `SIMULATORER` i skriptet. Endre dem der og kjør skriptet på nytt.

**Ny simulator:** legg HTML-filen i roten, legg til en oppføring i `SIMULATORER`, kjør skriptet og legg den til i `index.html`.

## Lenker

Simulatorene lenker til Verkstedhåndboka (`https://verkstedhandboka.vercel.app/#<emne>`). Håndboka lenker ikke tilbake.

## Deploy

Vercel publiserer fra grenen `main`. Oppsett: importer repoet, velg Framework Preset **Other**, la Build Command og Output Directory stå tomme.

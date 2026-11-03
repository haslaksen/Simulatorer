# RobotSekvens - kjør en robotsekvens skrevet som kode
#
# Elevoppgave: endre SEKVENS under, kjør scriptet og se roboten bevege seg.
# Navnene (A1, A2 ...) må være de samme som navnene på joints i Fusion.
# Akser som ikke er nevnt i et punkt, blir stående der de er.
# Vinklene under passer til GoFa-roboten fra LagRobot (alle akser 0 = hjem).
# En annen robot kan trenge andre vinkler: finn dem først med glidebryterne i RobotAkser.

import adsk.core
import adsk.fusion
import traceback
import math
import time

# ======== ENDRE HER ========

FART = 1.0        # sekunder per bevegelse
ANTALL_GANGER = 1 # hvor mange ganger sekvensen kjøres

SEKVENS = [
    {'A1': 0, 'A2': 0,  'A3': 0,  'A5': 0},   # Hjem
    {'A2': 20, 'A3': 30, 'A5': 40},           # Over delen
    {'A2': 35, 'A3': 35, 'A5': 20},           # Ned og grip
    {'A2': 20, 'A3': 30, 'A5': 40},           # Løft
    {'A1': 90},                               # Sving
    {'A2': 35, 'A3': 35, 'A5': 20},           # Ned og slipp
    {'A2': 20, 'A3': 30, 'A5': 40},           # Opp
    {'A1': 0, 'A2': 0,  'A3': 0,  'A5': 0},   # Hjem
]

# ===========================


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        ledd = {j.name: j for j in list(design.rootComponent.allJoints) + list(design.rootComponent.allAsBuiltJoints)
                if j.jointMotion.jointType == adsk.fusion.JointTypes.RevoluteJointType}

        # Sjekk at alle navn finnes
        ukjente = sorted({n for p in SEKVENS for n in p if n not in ledd})
        if ukjente:
            ui.messageBox('Finner ikke disse aksene: %s\n\nAkser i modellen: %s'
                          % (', '.join(ukjente), ', '.join(sorted(ledd))))
            return

        def begrens(v, j):
            lim = j.jointMotion.rotationLimits
            if lim.isMinimumValueEnabled:
                v = max(v, lim.minimumValue)
            if lim.isMaximumValueEnabled:
                v = min(v, lim.maximumValue)
            return v

        steg = max(2, int(FART * 25))
        for _ in range(ANTALL_GANGER):
            for punkt in SEKVENS:
                start = {n: ledd[n].jointMotion.rotationValue for n in punkt}
                mal = {n: begrens(math.radians(g), ledd[n]) for n, g in punkt.items()}
                for i in range(1, steg + 1):
                    t = 0.5 - 0.5 * math.cos(math.pi * i / steg)  # myk start og stopp
                    for n in punkt:
                        ledd[n].jointMotion.rotationValue = start[n] + (mal[n] - start[n]) * t
                    app.activeViewport.refresh()
                    adsk.doEvents()
                    time.sleep(FART / steg)
    except:
        ui.messageBox('Feil:\n{}'.format(traceback.format_exc()))

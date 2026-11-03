# RobotAkser - styr robotens akser (Revolute joints) med glidebrytere i Fusion
#
# Bruk:
#   1. Lag roboten med Revolute joints mellom leddene. Gi dem gjerne navn A1, A2, A3 ...
#      (aksene sorteres alfabetisk på navn).
#   2. Sett gjerne Joint Limits - da brukes de som min/maks på glidebryterne.
#   3. Utilities -> Scripts and Add-Ins -> kjør "RobotAkser".
#
# Knapper:
#   Hjem          - alle akser til 0 grader (eller "rest"-verdien fra Joint Limits)
#   Lagre punkt   - lagrer nåværende posisjon som et punkt i sekvensen
#   Kjør sekvens  - kjører gjennom alle lagrede punkter med myk bevegelse
#   Tøm sekvens   - sletter alle lagrede punkter

import adsk.core
import adsk.fusion
import traceback
import math
import time

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = 'robotAkserCmd'
handlers = []        # holder event-handlerne i live
ledd = []            # liste med Revolute joints
sekvens = []         # lagrede punkter: liste med vinkler (radianer), én per akse
oppdaterer = False   # hindrer at glidebryterne trigger seg selv


# ---------- Hjelpefunksjoner ----------

def finn_rotasjonsledd():
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        return []
    funnet = []
    for j in list(design.rootComponent.allJoints) + list(design.rootComponent.allAsBuiltJoints):
        if j.isSuppressed:
            continue
        if j.jointMotion.jointType == adsk.fusion.JointTypes.RevoluteJointType:
            funnet.append(j)
    funnet.sort(key=lambda j: j.name)
    return funnet


def grenser(j):
    lim = j.jointMotion.rotationLimits
    lo = lim.minimumValue if lim.isMinimumValueEnabled else -math.pi
    hi = lim.maximumValue if lim.isMaximumValueEnabled else math.pi
    return lo, hi


def hjemverdi(j):
    lim = j.jointMotion.rotationLimits
    if lim.isRestValueEnabled:
        return lim.restValue
    lo, hi = grenser(j)
    return min(max(0.0, lo), hi)


def begrens(v, j):
    lo, hi = grenser(j)
    return min(max(v, lo), hi)


def sett_vinkler(verdier):
    for j, v in zip(ledd, verdier):
        j.jointMotion.rotationValue = begrens(v, j)
    app.activeViewport.refresh()


def les_vinkler():
    return [j.jointMotion.rotationValue for j in ledd]


def oppdater_slidere(inputs):
    global oppdaterer
    oppdaterer = True
    try:
        for i, j in enumerate(ledd):
            s = adsk.core.FloatSliderCommandInput.cast(inputs.itemById('akse_%d' % i))
            if s:
                s.valueOne = begrens(j.jointMotion.rotationValue, j)
    finally:
        oppdaterer = False


def oppdater_sekvenstekst(inputs):
    tb = adsk.core.TextBoxCommandInput.cast(inputs.itemById('sekvenstekst'))
    if not tb:
        return
    if not sekvens:
        tb.text = 'Ingen punkter lagret'
        return
    linjer = []
    for n, punkt in enumerate(sekvens, start=1):
        deler = ['%s=%.0f°' % (j.name, math.degrees(v)) for j, v in zip(ledd, punkt)]
        linjer.append('P%d: ' % n + ', '.join(deler))
    tb.text = '\n'.join(linjer)


def kjor_sekvens(inputs):
    if not sekvens:
        ui.messageBox('Lagre minst ett punkt først.')
        return
    tid = adsk.core.FloatSpinnerCommandInput.cast(inputs.itemById('tid')).value
    steg = max(2, int(tid * 25))   # ca. 25 bilder per sekund
    punkter = [les_vinkler()] + sekvens
    for a, b in zip(punkter, punkter[1:]):
        for i in range(1, steg + 1):
            t = i / steg
            t = 0.5 - 0.5 * math.cos(math.pi * t)   # myk start og stopp
            sett_vinkler([va + (vb - va) * t for va, vb in zip(a, b)])
            adsk.doEvents()
            time.sleep(tid / steg)
    oppdater_slidere(inputs)


# ---------- Event-handlere ----------

class InputChangedHandler(adsk.core.InputChangedEventHandler):
    def notify(self, args):
        try:
            if oppdaterer:
                return
            ev = adsk.core.InputChangedEventArgs.cast(args)
            inp = ev.input
            inputs = ev.inputs

            if inp.id.startswith('akse_'):
                i = int(inp.id.split('_')[1])
                s = adsk.core.FloatSliderCommandInput.cast(inp)
                ledd[i].jointMotion.rotationValue = s.valueOne
                app.activeViewport.refresh()

            elif inp.id == 'hjem':
                sett_vinkler([hjemverdi(j) for j in ledd])
                oppdater_slidere(inputs)

            elif inp.id == 'lagre':
                sekvens.append(les_vinkler())
                oppdater_sekvenstekst(inputs)

            elif inp.id == 'kjor':
                kjor_sekvens(inputs)

            elif inp.id == 'tom':
                sekvens.clear()
                oppdater_sekvenstekst(inputs)
        except:
            ui.messageBox('Feil:\n{}'.format(traceback.format_exc()))


class ExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        pass   # posisjonene er allerede satt


class DestroyHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        adsk.terminate()


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            cmd = adsk.core.CommandCreatedEventArgs.cast(args).command
            cmd.okButtonText = 'Lukk'
            inputs = cmd.commandInputs

            gruppe = inputs.addGroupCommandInput('akser', 'Akser')
            gi = gruppe.children
            for i, j in enumerate(ledd):
                lo, hi = grenser(j)
                s = gi.addFloatSliderCommandInput('akse_%d' % i, j.name, 'deg', lo, hi, False)
                s.valueOne = begrens(j.jointMotion.rotationValue, j)

            inputs.addBoolValueInput('hjem', 'Hjem', False, '', False)

            sg = inputs.addGroupCommandInput('sekvensgruppe', 'Sekvens')
            si = sg.children
            si.addFloatSpinnerCommandInput('tid', 'Sek. per bevegelse', '', 0.2, 10.0, 0.1, 1.0)
            si.addBoolValueInput('lagre', 'Lagre punkt', False, '', False)
            si.addBoolValueInput('kjor', 'Kjør sekvens', False, '', False)
            si.addBoolValueInput('tom', 'Tøm sekvens', False, '', False)
            si.addTextBoxCommandInput('sekvenstekst', 'Punkter', 'Ingen punkter lagret', 6, True)

            for h, ev in ((InputChangedHandler(), cmd.inputChanged),
                          (ExecuteHandler(), cmd.execute),
                          (DestroyHandler(), cmd.destroy)):
                ev.add(h)
                handlers.append(h)
        except:
            ui.messageBox('Feil:\n{}'.format(traceback.format_exc()))


# ---------- Start ----------

def run(context):
    try:
        global ledd
        ledd = finn_rotasjonsledd()
        if not ledd:
            ui.messageBox('Fant ingen Revolute joints i designet.\n'
                          'Lag rotasjonsledd mellom robotens deler først.')
            return

        cmd_def = ui.commandDefinitions.itemById(CMD_ID)
        if cmd_def:
            cmd_def.deleteMe()
        cmd_def = ui.commandDefinitions.addButtonDefinition(
            CMD_ID, 'Robotakser', 'Styr robotens akser med glidebrytere')

        on_created = CommandCreatedHandler()
        cmd_def.commandCreated.add(on_created)
        handlers.append(on_created)

        cmd_def.execute()
        adsk.autoTerminate(False)   # hold scriptet i live mens dialogen er åpen
    except:
        ui.messageBox('Feil:\n{}'.format(traceback.format_exc()))

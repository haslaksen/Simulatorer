# LagRobot - bygger en forenklet ABB GoFa CRB 15000 (5 kg) i Fusion
#
# Scriptet lager et nytt design med:
#   - Fot (står fast), Sokkel (A1), Overarm (A2), Underarm (A3), Håndledd med griper (A5)
#   - fire rotasjonsledd (Revolute joints) som heter A1, A2, A3 og A5, med aksegrenser
#   - en kloss på A og en kasse på B, som i Robotarm-simulatoren
# Målene er fra ABBs produktspesifikasjon (forenklet). Alle akser på 0 = hjem, som på GoFa:
# overarmen rett opp og underarmen vannrett fram. A4 og A6 er ikke med.
# Etterpå kan du kjøre RobotAkser eller RobotSekvens.

import adsk.core
import adsk.fusion
import traceback
import math

# Mål i mm (samme som i simulatoren)
FOT = 100         # høyden på foten, der A1 sitter
SKULDER = 265     # høyde fra gulvet til A2
OVERARM = 444     # A2 til A3
KNEKK = 190       # underarmen går først rett opp fra A3 ...
UNDERARM = 470    # ... og så fram til håndleddet (A5)
GRIPER = 200      # flens og griper, fra A5 til TCP
REK = 597         # avstand fra foten til klossen og kassa

GRENSER = {'A1': (-180, 180), 'A2': (-180, 180), 'A3': (-225, 85), 'A5': (-180, 180)}  # fra ABB


def cm(mm):
    return mm / 10.0


def P(x, y, z):
    return adsk.core.Point3D.create(cm(x), cm(y), cm(z))


def boks(tbm, x, y, z, bx, by, bz):
    """Boks med sentrum (x, y, z) og mål bx, by, bz (mm)."""
    b = adsk.core.OrientedBoundingBox3D.create(P(x, y, z), adsk.core.Vector3D.create(1, 0, 0),
                                               adsk.core.Vector3D.create(0, 1, 0), cm(bx), cm(by), cm(bz))
    return tbm.createBox(b)


def sylinder(tbm, a, b, r):
    return tbm.createCylinderOrCone(a, cm(r), b, cm(r))


def legg_til(comp, kropper):
    bf = comp.features.baseFeatures.add()
    bf.startEdit()
    for k in kropper:
        comp.bRepBodies.add(k, bf)
    bf.finishEdit()


def ny_del(root, navn):
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = navn
    return occ


def leddpunkt(occ, x, z):
    """Et skissepunkt i (x, 0, z) mm, sett fra hele modellen."""
    comp = occ.component
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(cm(z)))
    plan = comp.constructionPlanes.add(pin)
    plan.isLightBulbOn = False
    sk = comp.sketches.add(plan)
    sk.isVisible = False
    p = sk.sketchPoints.add(sk.modelToSketchSpace(P(x, 0, z)))
    return adsk.fusion.JointGeometry.createByPoint(p.createForAssemblyContext(occ))


def lag_ledd(root, navn, bevegelig, fast, x, z, retning):
    inp = root.joints.createInput(leddpunkt(bevegelig, x, z), leddpunkt(fast, x, z))
    inp.setAsRevoluteJointMotion(retning)
    j = root.joints.add(inp)
    j.name = navn
    lo, hi = GRENSER[navn]
    lim = j.jointMotion.rotationLimits
    lim.isMinimumValueEnabled = True
    lim.minimumValue = math.radians(lo)
    lim.isMaximumValueEnabled = True
    lim.maximumValue = math.radians(hi)
    lim.isRestValueEnabled = True
    lim.restValue = 0
    return j


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent
        tbm = adsk.fusion.TemporaryBRepManager.get()

        A2z = SKULDER
        A3z = SKULDER + OVERARM
        Uz = A3z + KNEKK            # høyden på underarmen
        Wx = UNDERARM               # håndleddet A5 sitter i (Wx, 0, Uz)

        # Delene bygges i hjemstilling (alle akser 0)
        fot = ny_del(root, 'Fot')
        legg_til(fot.component, [boks(tbm, 0, 0, FOT / 2, 165, 165, FOT)])

        sokkel = ny_del(root, 'Sokkel A1')
        legg_til(sokkel.component, [sylinder(tbm, P(0, 0, FOT), P(0, 0, A2z), 75)])

        overarm = ny_del(root, 'Overarm A2')
        legg_til(overarm.component, [sylinder(tbm, P(0, -75, A2z), P(0, 75, A2z), 70),
                                     sylinder(tbm, P(0, 0, A2z), P(0, 0, A3z), 55)])

        underarm = ny_del(root, 'Underarm A3')
        legg_til(underarm.component, [sylinder(tbm, P(0, -65, A3z), P(0, 65, A3z), 60),
                                      sylinder(tbm, P(0, 0, A3z), P(0, 0, Uz), 50),
                                      sylinder(tbm, P(0, 0, Uz), P(Wx, 0, Uz), 45)])

        handledd = ny_del(root, 'Håndledd og griper A5')
        legg_til(handledd.component, [sylinder(tbm, P(Wx, -50, Uz), P(Wx, 50, Uz), 45),
                                      sylinder(tbm, P(Wx, 0, Uz), P(Wx + 100, 0, Uz), 32),
                                      boks(tbm, Wx + 110, 0, Uz, 20, 40, 120),
                                      boks(tbm, Wx + 160, 0, Uz + 50, 80, 20, 14),
                                      boks(tbm, Wx + 160, 0, Uz - 50, 80, 20, 14)])

        # Kloss på A (retning X) og kasse på B (retning Y), står fast
        bord = ny_del(root, 'Kloss A og kasse B')
        k, v, h = 250, 8, 150
        legg_til(bord.component, [boks(tbm, REK, 0, 50, 100, 100, 100),
                                  boks(tbm, 0, REK, 3, k, k, 6),
                                  boks(tbm, -k / 2 + v / 2, REK, h / 2, v, k, h),
                                  boks(tbm, k / 2 - v / 2, REK, h / 2, v, k, h),
                                  boks(tbm, 0, REK - k / 2 + v / 2, h / 2, k, v, h),
                                  boks(tbm, 0, REK + k / 2 - v / 2, h / 2, k, v, h)])
        fot.isGrounded = True
        bord.isGrounded = True

        # Rotasjonsleddene
        Z = adsk.fusion.JointDirections.ZAxisJointDirection
        Y = adsk.fusion.JointDirections.YAxisJointDirection
        lag_ledd(root, 'A1', sokkel, fot, 0, FOT, Z)
        lag_ledd(root, 'A2', overarm, sokkel, 0, A2z, Y)
        a3 = lag_ledd(root, 'A3', underarm, overarm, 0, A3z, Y)
        lag_ledd(root, 'A5', handledd, underarm, Wx, Uz, Y)

        # Sjekk at pluss-vinkel på A3 vipper underarmen ned, som på GoFa og i simulatoren
        a3.jointMotion.rotationValue = math.radians(30)
        tupp = P(Wx, 0, Uz)
        tupp.transformBy(underarm.transform2)
        a3.jointMotion.rotationValue = 0
        app.activeViewport.fit()

        if tupp.z > cm(Uz):
            ui.messageBox('Roboten er laget, men A2, A3 og A5 går motsatt vei av simulatoren.\n'
                          'Sett minus foran vinklene til A2, A3 og A5 i koden, eller si fra til læreren.')
        else:
            ui.messageBox('Roboten (forenklet ABB GoFa) er laget!\n\nLeddene heter A1, A2, A3 og A5. '
                          'Alle på 0 er hjem.\nKjør nå RobotAkser (glidebrytere) eller RobotSekvens (punktene dine).')
    except:
        ui.messageBox('Feil:\n{}'.format(traceback.format_exc()))

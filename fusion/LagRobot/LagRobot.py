# LagRobot - bygger en enkel robotarm med tre akser i Fusion
#
# Scriptet lager et nytt design med:
#   - Fot (står fast), Sokkel (A1), Overarm (A2), Underarm med griper (A3)
#   - tre rotasjonsledd (Revolute joints) som heter A1, A2 og A3, med aksegrenser
#   - en kloss på A og en kasse på B, som i Robotarm-simulatoren
# Målene passer til simulatoren. Etterpå kan du kjøre RobotAkser eller RobotSekvens.

import adsk.core
import adsk.fusion
import traceback
import math

# Mål i mm (samme som i simulatoren)
SKULDER = 192     # høyde fra gulvet til A2
OVERARM = 500     # A2 til A3
UNDERARM = 440    # A3 til griperen
GRIPER = 120      # griperen, til TCP
REK = 512         # avstand fra foten til klossen og kassa

GRENSER = {'A1': (-170, 170, 0), 'A2': (-30, 90, 0), 'A3': (0, 150, 90)}  # min, maks, hjem


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


def leddpunkt(occ, z):
    """Et skissepunkt på aksen i høyde z (mm), sett fra hele modellen."""
    comp = occ.component
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(cm(z)))
    plan = comp.constructionPlanes.add(pin)
    plan.isLightBulbOn = False
    sk = comp.sketches.add(plan)
    sk.isVisible = False
    p = sk.sketchPoints.add(sk.modelToSketchSpace(P(0, 0, z)))
    return adsk.fusion.JointGeometry.createByPoint(p.createForAssemblyContext(occ))


def lag_ledd(root, navn, bevegelig, fast, z, retning):
    inp = root.joints.createInput(leddpunkt(bevegelig, z), leddpunkt(fast, z))
    inp.setAsRevoluteJointMotion(retning)
    j = root.joints.add(inp)
    j.name = navn
    lo, hi, hjem = GRENSER[navn]
    lim = j.jointMotion.rotationLimits
    lim.isMinimumValueEnabled = True
    lim.minimumValue = math.radians(lo)
    lim.isMaximumValueEnabled = True
    lim.maximumValue = math.radians(hi)
    lim.isRestValueEnabled = True
    lim.restValue = math.radians(hjem)
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
        Gz = A3z + UNDERARM

        # Delene bygges med armen rett opp (alle vinkler 0)
        fot = ny_del(root, 'Fot')
        legg_til(fot.component, [sylinder(tbm, P(0, 0, 0), P(0, 0, 40), 150)])

        sokkel = ny_del(root, 'Sokkel A1')
        legg_til(sokkel.component, [sylinder(tbm, P(0, 0, 40), P(0, 0, A2z - 40), 100),
                                    boks(tbm, 0, 0, A2z - 20, 120, 160, 80)])

        overarm = ny_del(root, 'Overarm A2')
        legg_til(overarm.component, [sylinder(tbm, P(0, -70, A2z), P(0, 70, A2z), 60),
                                     boks(tbm, 0, 0, (A2z + A3z) / 2, 80, 80, OVERARM)])

        underarm = ny_del(root, 'Underarm og griper A3')
        legg_til(underarm.component, [sylinder(tbm, P(0, -55, A3z), P(0, 55, A3z), 50),
                                      boks(tbm, 0, 0, (A3z + Gz) / 2, 60, 60, UNDERARM),
                                      boks(tbm, 0, 0, Gz + 10, 120, 50, 20),
                                      boks(tbm, -52, 0, Gz + 20 + (GRIPER - 20) / 2, 16, 40, GRIPER - 20),
                                      boks(tbm, 52, 0, Gz + 20 + (GRIPER - 20) / 2, 16, 40, GRIPER - 20)])

        # Kloss på A (retning X) og kasse på B (retning Y), står fast
        bord = ny_del(root, 'Kloss A og kasse B')
        k, v, h = 248, 8, 152
        legg_til(bord.component, [boks(tbm, REK, 0, 52, 96, 96, 104),
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
        a1 = lag_ledd(root, 'A1', sokkel, fot, 40, Z)
        a2 = lag_ledd(root, 'A2', overarm, sokkel, A2z, Y)
        a3 = lag_ledd(root, 'A3', underarm, overarm, A3z, Y)

        # Sjekk at pluss-vinkel på A2 vipper armen fram (mot klossen), som i simulatoren
        a2.jointMotion.rotationValue = math.radians(30)
        tupp = P(0, 0, Gz)
        tupp.transformBy(underarm.transform2)
        a2.jointMotion.rotationValue = 0
        a3.jointMotion.rotationValue = math.radians(90)   # hjem: A1 0, A2 0, A3 90
        app.activeViewport.fit()

        if tupp.x < 0:
            ui.messageBox('Roboten er laget, men A2 og A3 går motsatt vei av simulatoren.\n'
                          'Bruk minus foran vinklene til A2 og A3, eller si fra til læreren.')
        else:
            ui.messageBox('Roboten er laget!\n\nLeddene heter A1, A2 og A3.\n'
                          'Kjør nå RobotAkser (glidebrytere) eller RobotSekvens (punktene dine).')
    except:
        ui.messageBox('Feil:\n{}'.format(traceback.format_exc()))

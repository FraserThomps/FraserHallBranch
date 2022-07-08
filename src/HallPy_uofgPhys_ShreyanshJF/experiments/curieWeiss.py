from ..helper import reconnectInstructions
from .__init__ import getAndSetupExpInsts

requiredEquipment = {
    "LCR Meter": [
        {"purpose": "Capacitance", "var": "lcr"}
    ],
    "Multimeter": [
        {"purpose": "Temperature", "var": "mm", "config": ["CONF:TCO", "TCO:TYPE T"]}
    ],
}
expName = "Curie Weiss Lab"


def setup(instruments=None, serials=None, inGui=False):
    if serials is None:
        serials = {}
    if instruments is None:
        instruments = []

    if len(instruments) == 0:
        print("\x1b[;43m No instruments could be recognised / contacted \x1b[m")
        print("")
        reconnectInstructions(inGui)
        raise Exception("No instruments could be recognised / contacted")

    foundReqInstruments = getAndSetupExpInsts(requiredEquipment, instruments, serials, inGui)

    print("\x1b[;42m Instruments ready to use for Curie Weiss experiment \x1b[m")
    print("Proceed as shown:")
    if inGui:
        print("   1 | cwInstruments = HallPy_Teach()")
        print("   2 | data = placeHolderExperimentFunction(cwInstruments)")
    else:
        print("   1 | cwInstruments = hp.curieWeiss.setup(instruments)")
        print("   2 | data = placeHolderExperimentFunction(cwInstruments)")
    print(' ')
    print("\x1b[;43m NOTE : If any instruments are disconnected or turned off after     \x1b[m")
    print("\x1b[;43m        this point you will have to restart and reconnect them      \x1b[m")
    if inGui:
        print("\x1b[;43m        to the PC and rerun the `HallPy_Tech()` function            \x1b[m")
    else:
        print("\x1b[;43m        to the PC and rerun 'hp.initInstruments()' and              \x1b[m")
        print("\x1b[;43m        hp.curieWeiss.setup()                                       \x1b[m")

    return foundReqInstruments

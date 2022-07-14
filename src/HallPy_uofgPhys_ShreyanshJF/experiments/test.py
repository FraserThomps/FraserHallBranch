from ..helper import reconnectInstructions
from .__init__ import getAndSetupExpInsts

requiredEquipment = {
    "LCR Meter": [
        {"purpose": "Capacitance", "var": "lcr"}
    ],
    "Multimeter": [
        {"purpose": "Temperature", "var": "mm", "config": ["CONF:TCO", "TCO:TYPE T"]}
    ],
    "Power Supply": [
        {"purpose": "Test Power Supple 1", "var": "ps1"},
        {"purpose": "Test Power Supple 2", "var": "ps2"}
    ],
}
expName = "Test"


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

    print("\x1b[;42m The test instruments were setup successfully \x1b[m")

    return foundReqInstruments


def doExperiment():
    print("TEST")

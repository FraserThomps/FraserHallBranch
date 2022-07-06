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


def setup(instruments=None, lcr=0, mm=0, inGui=False):
    if instruments is None:
        instruments = []

    serials = {}
    if lcr != 0:
        serials["lcr"] = str(lcr)
    if mm != 0:
        serials["mm"] = str(mm)

    if len(instruments) == 0:
        print("\x1b[;43m No instruments could be recognised / contacted \x1b[m")
        print("")
        reconnectInstructions(inGui)
        raise Exception("No instruments could be recognised / contacted")

    foundReqInstruments = getAndSetupExpInsts(requiredEquipment, instruments, serials, inGui)

    print("\x1b[;42m Instruments ready to use for Curie Weiss experiment \x1b[m")
    print("This is a test")

    return foundReqInstruments

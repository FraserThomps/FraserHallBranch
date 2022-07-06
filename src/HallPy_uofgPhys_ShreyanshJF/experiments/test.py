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


def setup(instruments=None, ps1=0, ps2=0, inGui=False):
    if instruments is None:
        instruments = []

    serials = {}
    if ps1 != 0:
        serials["ps1"] = str(ps1)
    if ps2 != 0:
        serials["ps2"] = str(ps2)

    if len(instruments) == 0:
        print("\x1b[;43m No instruments could be recognised / contacted \x1b[m")
        print("")
        reconnectInstructions(inGui)
        raise Exception("No instruments could be recognised / contacted")

    foundReqInstruments = getAndSetupExpInsts(requiredEquipment, instruments, serials, inGui)

    print("\x1b[;42m Instruments ready to use for Curie Weiss experiment \x1b[m")
    print("This is a test")

    return foundReqInstruments

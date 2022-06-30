import time

from .helper import _requiredInstrumentNotFound, reconnectInstructions, getInstTypeCount, sortArrByKey

requiredEquipment = {
    "LCR Meter": [("Capacitance", "lcr")],
    "Multimeter": [("Temperature", "mm")],
}


def setup(instruments=None, lcr=0, mm=0, inGui=False):
    if instruments is None:
        instruments = []
    if lcr != 0:
        lcr = str(lcr)
    if mm != 0:
        mm = str(mm)

    if len(instruments) == 0:
        print("\x1b[;43m No instruments could be recognised / contacted \x1b[m")
        print('')
        reconnectInstructions(inGui)
        raise Exception("No instruments could be recognised / contacted")

    instTypeCount = getInstTypeCount(instruments)
    cwLcr = []
    cwMM = {}

    for instType in instTypeCount.keys():
        if instType in requiredEquipment.keys():
            if instTypeCount[instType] == 0:
                _requiredInstrumentNotFound(instType, inGui)
                raise Exception("No " + instType + " connected")
            elif instTypeCount[instType] > 1 and (lcr if instType == "LCR Meter" else mm) == 0:
                print("\x1b[;41m Multiple " + instType + "s connected \x1b[m")
                print("Please provide serial number of the " + instType + " to be used")
                print("Example: ")
                print("   1 | cwInsts = cw.setupCW(instruments, lcr='XXXXXXXXX', mm='XXXXXXX')")
                print("\x1b[;43m NOTE: you will find the serial number on a tag on the instrument \x1b[m")
                raise Exception(instType + " serial number was not provided")
            elif instTypeCount[instType] > 1 and type((lcr if instType == "LCR Meter" else mm)) == str:
                foundInst = list(filter(lambda d: (lcr if instType == "LCR Meter" else mm) in d["name"], instruments))
                if len(foundInst) != 1:
                    if inGui:
                        print("\x1b[;41m Please contact your lab technician or a professor \x1b[m")
                    else:
                        print("\x1b[;41m No " + instType + " with SN:" + (
                            lcr if instType == "LCR Meter" else mm) + "found "
                                                                      "\x1b[m")
                        print("Pleae check that you are using the correct serial number")
                        print("Available " + instType + "(s):")
                        availableINsts = sortArrByKey(instruments, 'type', instType)
                        for inst in availableINsts:
                            print("    " + inst['name'].replace('\n', ' '))
                    raise Exception(instType + " serial number missmatch")
                if instType == "LCR Meter":
                    cwLcr = foundInst[0]
                elif instType == "Multimeter":
                    cwMM = foundInst[0]
            else:
                if instType == "LCR Meter":
                    cwLcr = list(filter(lambda d: "LCR Meter" in d["name"], instruments))
                elif instType == "Multimeter":
                    cwMM = list(filter(lambda d: "Multimeter" in d["name"], instruments))

    cwMM['inst'].write("CONF:TCO")
    time.sleep(0.2)
    cwMM['inst'].wite("TCO:TYPE T")

    print("\x1b[;42m Instruments ready to use for Curie Weiss experiment \x1b[m")
    print("Procede as shown:")
    if inGui:
        print("   1 | insts = HallPy_Teach()")
        print("   2 | data = placeHolderExperimentFunction(insts)")
    else:
        print("   1 | cwInsts = hp.curieWeiss.setup(instruments, lcr='XXXXXXXXX', mm='XXXXXXX')")
        print("   2 | data = placeHolderExperimentFunction(insts)")
    print(' ')
    print("\x1b[;43m NOTE : If any instruments are disconnected or turned off after     \x1b[m")
    print("\x1b[;43m        this point you will have to restart and reconnect them      \x1b[m")
    if inGui:
        print("\x1b[;43m        to the PC and rerun the `HallPy_Tech()` function            \x1b[m")
    else:
        print("\x1b[;43m        to the PC and rerun 'initInstruments()' and setupCW()       \x1b[m")

    return {
        'lcr': cwLcr,
        'mm': cwMM
    }

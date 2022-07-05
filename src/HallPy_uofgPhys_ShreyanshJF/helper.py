import numpy as np
from .constants import supportedInstruments


def sortArrByKey(arr, key, val):
    return list(filter(lambda d: d[str(key)] == val, arr))


def reconnectInstructions(inGui=False):
    print("\x1b[;43m NOTE : If instruments aren't recognised, follow instructions below: \x1b[m")
    print("  - Disconnect USB / USB hub from PC")
    print("  - Restart kernel (From top menu : Kernel > Restart & Clear Outputs)")
    print("  - Restart Instrument")
    print("  - Connect USB / USB hub to PC")

    if inGui:
        print("  - Press the `Restart Setup` button or rerun the `HallPy_Teach()` function.")
    else:
        print("  - Rerun the `initInstruments()` function.")

    print("*Follow instructions in provided order.")


def getInstTypeCount(instruments):
    instTypeCount = supportedInstruments.copy()

    for instrumentType in instTypeCount:
        instTypeCount[instrumentType] = np.size(sortArrByKey(instruments, 'type', instrumentType))

    instTypeCount['Unknown'] = np.size(sortArrByKey(instruments, 'type', 'Unknown'))

    return instTypeCount


def _requiredInstrumentNotFound(instType, inGui=False):
    print("\x1b[;41m No " + instType + " is connected. \x1b[m")
    print("Please plug in a " + instType + " via USB to the PC.")
    if inGui:
        print("\x1b[;43m NOTE : You will have to click the `Restart Setup` button or rerun the `HallPy_Teach()` "
              "function after plugging in the " + instType + ". \x1b[m")
    else:
        print("\x1b[;43m NOTE : You will have to rerun the `initInstruments()` function after plugging in the "
              + instType + ". \x1b[m")


def _notEnoughReqInstType(instType, requiredEquipment, instruments, inGui=False):
    instTypeCount = getInstTypeCount(instruments)
    if instTypeCount[instType] == 0:
        print("\x1b[;41m No " + instType + " found. \x1b[m")
    else:
        print("\x1b[;41m Only " + str(instTypeCount[instType]) + " " + instType + "(s) found. \x1b[m")
    if len(requiredEquipment[instType]) == 1:
        print(str(len(requiredEquipment[instType])), instType, "is required for this experiment.")
    else:
        print(str(len(requiredEquipment[instType])), instType + "(s) are required for this experiment.")
    print("Please plug the required number of " + instType + "(s) to the PC via USB. ")
    if not inGui:
        print(' ')
        print("\x1b[;43m NOTE : You will have to rerun the `initInstruments()` function after \x1b[m")
        print("\x1b[;43m        plugging in the " + instType + "(s).                          \x1b[m")


__all__ = [reconnectInstructions, sortArrByKey]

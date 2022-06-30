import numpy as np

from src.HallPy_uofgPhys_ShreyanshJF import supportedInstruments


def sortArrByKey(arr, key, val):
    return list(filter(lambda d: d[str(key)] == val, arr))


def reconnectInstructions(inGui=False):
    print("\x1b[;43m NOTE : If instruments aren't recognised, follow instructions below \x1b[m")
    print(" - Disconnect USB / USB hub from PC")
    print(" - Restart kernel (From top menu : Kernel > Restart & Clear Outputs)")
    print(" - Restart Instrument")
    print(" - Connect USB / USB hub to PC")

    if inGui:
        print(" - Press the `Restart Setup` button or rerun the `HallPy_Teach()` function")
    else:
        print(" - Rerun the `initInstruments()` function")

    print("*Follow instructions in provided order")


def getInstTypeCount(instruments):
    instTypeCount = supportedInstruments.copy()

    for instrumentType in instTypeCount:
        instTypeCount[instrumentType] = np.size(sortArrByKey(instruments, 'type', instrumentType))

    instTypeCount['Unknown'] = np.size(sortArrByKey(instruments, 'type', 'Unknown'))

    return instTypeCount


def _noInstrumentsFound(inGui):
    print("\x1b[;41m No instruments found")


def _requiredInstrumentNotFound(instType, inGui=False):
    print("\x1b[;41m No " + instType + " is connected \x1b[m")
    print("Please plug in a " + instType + " via USB to the PC")
    if inGui:
        print("\x1b[;43m NOTE : You will have to click the `Restart Setup` button or rerun the `HallPy_Teach()` "
              "function after plugging in the " + instType + " \x1b[m")
    else:
        print("\x1b[;43m NOTE : You will have to rerun the `initInstruments()` function after plugging in the "
              + instType + " \x1b[m")


__all__ = [_noInstrumentsFound, reconnectInstructions, sortArrByKey, getInstTypeCount]

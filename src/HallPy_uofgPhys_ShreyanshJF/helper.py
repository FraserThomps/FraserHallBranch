import time

import numpy as np
from pyvisa import VisaIOError

from .constants import supportedInstruments


def sortArrByKey(arr, key, val):
    return list(filter(lambda d: d[str(key)] == val, arr))


def reconnectInstructions(inGui=False):
    print("\x1b[;43m NOTE : If instruments aren't recognised, follow instructions below: \x1b[m")
    print(" - Disconnect USB / USB hub from PC")
    print(" - Restart kernel (From top menu : Kernel > Restart & Clear Outputs)")
    print(" - Restart Instrument")
    print(" - Connect USB / USB hub to PC")

    if inGui:
        print(" - Press the `Restart Setup` button or rerun the `HallPy_Teach()` function.")
    else:
        print(" - Rerun the `initInstruments()` function.")

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
    print("\x1b[;41m Only " + str(instTypeCount(instType)) + " " + instType + "(s) found. \x1b[m")
    print(str(len(requiredEquipment[instType])) + " are required for this experiment.")
    print("Please plug the required number of " + instType + "(s) to the PC via USB. ")
    if inGui:
        print("\x1b[;43m NOTE : You will have to click the `Restart Setup` button or rerun the `HallPy_Teach()` "
              "function after plugging in the " + instType + ". \x1b[m")
    else:
        print("\x1b[;43m NOTE : You will have to rerun the `initInstruments()` function after plugging in the "
              + instType + ". \x1b[m")


def getAndSetupExpInsts(requiredEquipment=None, instruments=None, serials=None, inGui=False):
    if serials is None:
        serials = {}
    if requiredEquipment is None:
        requiredEquipment = {}
    if instruments is None:
        instruments = []
    if len(requiredEquipment) == 0:
        return

    if len(instruments) == 0:
        print("\x1b[;43m No instruments could be recognised / contacted. \x1b[m")
        print("")
        reconnectInstructions(inGui)
        raise Exception("No instruments could be recognised / contacted.")

    instTypeCount = getInstTypeCount(instruments)
    expInstruments = {}

    for instType in requiredEquipment.keys():
        if instType not in instTypeCount.keys():
            _requiredInstrumentNotFound(instType, inGui)
            raise Exception("No " + instType + " connected")
        elif instTypeCount[instType] < len(requiredEquipment[instType]):
            _notEnoughReqInstType(instType, requiredEquipment, instruments, inGui)
            raise Exception("Not enough " + instType + "(s) connected.", str(len(requiredEquipment[instType])),
                            " required.")
        else:
            for instNeeded in requiredEquipment[instType]:
                instNeededObj = {
                    "res": {},
                    "type": instType,
                    "purpose": instNeeded['purpose'],
                    "config": instNeeded['config']
                }
                expInstruments[instNeeded["var"]] = instNeededObj
                if instTypeCount[instType] == 1 and len(requiredEquipment[instType]) == 1:
                    expInstruments[instNeeded["var"]]["res"] = sortArrByKey(instruments, 'type', instType)[0]
                elif instNeeded["var"] not in serials.keys() and instTypeCount[instType] > 1:
                    print("\x1b[;43m Please provide the serial number(s) for the " + instType + " to be used for "
                          + instNeededObj["purpose"] + " measurement. \x1b[m")
                    print("Required variable: '" + instNeeded["var"] + "'")
                    raise Exception("Missing serial numbers for " + instType + " assignment.")
                else:
                    serial = serials[instNeeded["var"]]
                    foundInsts = list(filter(lambda instrument: serial in instrument['name'], instruments))
                    if len(foundInsts) == 0:
                        print("\x1b[;43m  Please use a valid serial number for the " + instType + ". \x1b[m")
                        print("Serial number entered: " + serial)
                        print("Found Instruments | " + instType + "(s) : ")
                        print("Available " + instType + "(s): ")
                        for inst in sortArrByKey(instruments, 'type', instType):
                            print("   " + inst['name'].replace("\n", " "))
                            print(" ")
                        raise Exception("No instruments with given serial number found.")
                    elif len(foundInsts) != 1:
                        print("\x1b[;43m  Please call a Lab Technician or IT support. \x1b[m")
                        print("Multiple instruments with same serial number found")
                        print("Serial number in question: " + serial)
                        print("Found Instruments | " + instType + "(s) : ")
                        for inst in foundInsts:
                            print("   " + inst['name'].replace("\n", " "))
                            print("USB Resource Name: " + inst['resName'])
                            print(" ")
                        print("All connected Instruments: ")
                        for inst in instruments:
                            print("   " + inst['name'].replace("\n", " "))
                            print("USB Resource Name: " + inst['resName'])
                            print("Type: " + inst["type"])
                            print(" ")
                        raise Exception("Multiple instruments with same serial number found.")
                    else:
                        expInstruments[instNeeded["var"]]["res"] = foundInsts[0]
                for confLine in instNeeded['config']:
                    try:
                        instNeeded['res'].write(confLine)
                        time.sleep(0.2)
                    except VisaIOError:
                        print("\x1b[;43m Error occurred while configuring " + instNeeded['type'] + " for "
                              + instNeeded['purpose'] + " measurement. ")
                        print("Please check experiment config lines")
                        raise
    return expInstruments


__all__ = [reconnectInstructions, sortArrByKey, getInstTypeCount]

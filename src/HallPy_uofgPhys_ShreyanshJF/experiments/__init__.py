"""
HallPy_Teach.experiments: experiments which work with HallPy_Teach Library
===================================================================================

Documentation is available in the docstrings and online at:
https://hallPy.fofandi.dev/expriments.

Description
-----------
HallPy_Teach uses the pyvisa package to communicate with lab equipment. It is intended to be used as an CAI (Computer
Assisted Instruction) library to let students get setup with labs in a straight forward way. It exposes functions which
can be used to develop any type of computer operated lab if the lab equipment operates on the VISA specifications
and is supported by pyvisa.

Notes
-----
This library can be used either through the terminal (Command Line) or Jupyter Lab / Notebook. More details can be
found on the online at https://hallPy.fofandi.dev.

See Also
----------
+ getAndSetupExpInsts(*args)

"""

import time

from pyvisa import VisaIOError

from ..helper import _requiredInstrumentNotFound, _notEnoughReqInstType, sortArrByKey
from ..helper import reconnectInstructions, getInstTypeCount


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
                    "purpose": instNeeded["purpose"]
                }
                if "config" in instNeeded.keys():
                    if len(instNeeded["config"]) > 0:
                        instNeededObj["config"] = instNeeded["config"]

                if instTypeCount[instType] == 1 and len(requiredEquipment[instType]) == 1:
                    instNeededObj["res"] = sortArrByKey(instruments, "type", instType)[0]
                    print(instNeededObj['purpose'], instNeededObj['type'])
                    print(instNeededObj["res"])
                elif instNeeded["var"] not in serials.keys() and instTypeCount[instType] > 1:
                    print("\x1b[;43m Please provide the serial number(s) for the " + instType + " to be used for "
                          + instNeededObj["purpose"] + " measurement. \x1b[m")
                    print("Required variable: '" + instNeeded["var"] + "'")
                    raise Exception("Missing serial numbers for " + instType + " assignment.")
                else:
                    serial = serials[instNeeded["var"]]
                    foundInsts = list(filter(lambda instrument: serial in instrument["name"], instruments))
                    if len(foundInsts) == 0:
                        print("\x1b[;43m  Please use a valid serial number for the " + instType + ". \x1b[m")
                        print("Serial number entered: " + serial)
                        print("Found Instruments | " + instType + "(s) : ")
                        print("Available " + instType + "(s): ")
                        for inst in sortArrByKey(instruments, "type", instType):
                            print("   " + inst["name"].replace("\n", " "))
                            print(" ")
                        raise Exception("No instruments with given serial number found.")
                    elif len(foundInsts) != 1:
                        print("\x1b[;43m  Please call a Lab Technician or IT support. \x1b[m")
                        print("Multiple instruments with same serial number found")
                        print("Serial number in question: " + serial)
                        print("Found Instruments | " + instType + "(s) : ")
                        for inst in foundInsts:
                            print("   " + inst["name"].replace("\n", " "))
                            print("USB Resource Name: " + inst["resName"])
                            print(" ")
                        print("All connected Instruments: ")
                        for inst in instruments:
                            print("   " + inst["name"].replace("\n", " "))
                            print("USB Resource Name: " + inst["resName"])
                            print("Type: " + inst["type"])
                            print(" ")
                        raise Exception("Multiple instruments with same serial number found.")
                    else:
                        instNeededObj["res"] = foundInsts[0]
                        print(instNeededObj['purpose'], instNeededObj['type'])
                        print(instNeededObj["res"])

                if "config" in instNeeded.keys():
                    for confLine in instNeededObj["config"]:
                        try:
                            instNeededObj["res"].write(confLine)
                            time.sleep(0.2)
                        except VisaIOError:
                            print("\x1b[;43m Error occurred while configuring " + instNeededObj["type"] + " for "
                                  + instNeededObj["purpose"] + " measurement. \x1b;m")
                            print("Config in question: '" + confLine + "'.")
                            print("Please check experiment config lines.")
                            raise
                        except:
                            print("\x1b[;43m Error occurred while configuring " + instNeededObj["type"] + " for "
                                  + instNeededObj["purpose"] + " measurement. \x1b;m")
                            print("Config in question: '" + confLine + "'.")
                            print("Please check experiment config lines.")
                            raise
                expInstruments[instNeeded["var"]] = instNeededObj

    return expInstruments

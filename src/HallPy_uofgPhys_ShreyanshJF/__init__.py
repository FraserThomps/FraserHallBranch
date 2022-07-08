"""
HallPy_Teach: A Python package to aid physics students in performing lab activities
===================================================================================

Documentation is available in the docstrings and online at:
https://hallPy.fofandi.dev.

Description ----------- HallPy_Teach uses the pyvisa package to communicate with lab equipment. It is intended to be
used as an CAI (Computer Assisted Instruction) library to let students get setup with labs in a straight forward way.
It exposes functions which can be used to develop any type of computer operated lab if the lab equipment operates on
the VISA specifications and is supported by pyvisa.

Notes
-----
This library can be used either through the terminal (Command Line) or Jupyter Lab / Notebook. More details can be
found on the online at https://hallPy.fofandi.dev.

Submodules
----------
+ experiments/

"""
import re

import pyvisa
from .experiments import curieWeiss, hallEffect, test
from IPython.core.display import display
from IPython.display import clear_output
import ipywidgets as widgets

from .constants import supportedInstruments, serialRegex
from .helper import reconnectInstructions, getInstTypeCount, sortArrByKey

allExperiments = [
    curieWeiss,
    hallEffect,
    test
]


def initInstruments(inGui=False):
    """Initializing and recognising connected equipment.

    Function does the setup for any of the experiments which use this HallPy_Teach. It recognises the connected
    instruments and provides the instruments in the form of the `inst` object. It also classifies the equipment by their
    uses depending on the manufacturer & model. Equipment is queried using the pyvisa library (`inst.query("*IDN?")`).

    The list of supported instruments is in the constants' module (mentioned in the See Also section).

    See Also
    --------
    + constants.supportedEquipment : Used to classify instrument
    + HallPy_Teach() : Used to use library with GUI in Jupyter Notebook / Lab

    Returns
    -------
    Array of objects containing information about the connected instruments
    Example of 2 found instruments:
    [
        {
            'inst': USBInstrument, #PyVisa Object: to be used to communicate with instrument eg.:
            multimeter['inst'].query('*IDN?')

            'name': 'KEITHLEY INSTRUMENTS INC.,MODEL 2110,8014885,02.03-03-20', #String: Name of instrument from
            inst.query('*IDN?')

            'resName': 'USB0::0x5E6::0x2110::8014885::INSTR', #String: Name of instrument USB resource

            'type': 'Multimeter' #Strign: Type of instrument. other types: 'LCR Meter', 'Power Supply'
        },
        {
            'inst': SerialInstrument,                     #PyVisa Object

            'name': 'B&K Precision ,891,468L20200...',    #String

            'resName': 'ASLR::INSTR',                     #String

            'type': 'LCR Meter'                           #String
        }
    ]
    """
    rm = pyvisa.ResourceManager()
    resList = rm.list_resources()
    instruments = []

    # Looping through all connected USB devices to look for usable instruments
    for res in resList:
        try:
            # Initiating communication with instrument
            instResource = rm.open_resource(res)

            # Getting instrument name - if successful, it is supported by PyVisa and is an Instrument not just
            # another USB device
            name = instResource.query("*IDN?")

            # Creating the instrument object to be used in the rest of the library
            inst = {
                "inst": instResource,
                "name": name,
                "resName": res
            }

            # Defining instrument type (see supported instruments in hp.constants.supportedInstruments)
            for instrumentType in supportedInstruments.keys():
                for supportedInstrumentName in supportedInstruments[instrumentType]:
                    if supportedInstrumentName in name:
                        inst['type'] = instrumentType

            # Defining instrument type as Unknown if instrument cannot be classified
            if len(inst.keys()) == 3:
                inst["type"] = "Unknown"

            # Adding instrument to the list of all instruments usable by HallPy_Teach_uofgPhys
            instruments.append(inst)

        # Error indicates that the USB device is incompatible with PyVisa
        except pyvisa.VisaIOError:
            pass
        finally:
            pass

    # Getting instrument count by instrument type
    instTypeCount = getInstTypeCount(instruments)

    # Raising error if no instruments are connected.
    if all(instrumentCount == 0 for instrumentCount in instTypeCount.values()):
        print("\x1b[;43m No instruments could be recognised / contacted \x1b[m")
        print('')
        reconnectInstructions(inGui)
        raise Exception("No instruments could be recognised / contacted")
    else:
        # Showing connected instruments to user
        countStr = ""
        for instrumentType in instTypeCount.keys():
            if instTypeCount[instrumentType] != 0:
                countStr = countStr + str(instTypeCount[instrumentType]) + " " + instrumentType + "(s)   "

        print(countStr)
        print('')
        reconnectInstructions(inGui)

        # Returning array of instruments : See documentation at the start of the function.
        return instruments


def HallPy_Teach(btn=None):
    if btn is None:
        btn = {}
    clear_output()
    instruments = initInstruments(inGui=True)

    expChoices = []
    for experiment in allExperiments:
        expChoices.append((experiment.expName, experiment))

    pickExpDropdown = widgets.Dropdown(options=expChoices, disabled=False)
    submitBtn = widgets.Button(description="Setup Experiment", icon="flask")
    onStartWidgets = [pickExpDropdown, submitBtn]

    restartSetupBtn = widgets.Button(
        description="Restart Setup",
        icon="play",
        disabled=True
    )

    print(" ")
    print("Choose experiment to perform")
    # noinspection PyTypeChecker
    display(widgets.VBox(onStartWidgets))

    def getUserSerialAssignment(expSetupFunc, expReq, availableInsts, expName):
        serials = {}
        serialDropdownsByType = {}
        for instType in expReq.keys():
            serialDropdownsByType[instType] = {}
            if len(expReq[instType]) > 1:
                print("Assign", instType + "(s)")
                availableSerials = []
                for inst in sortArrByKey(availableInsts, "type", instType):
                    regex = ""
                    for instPartialName in serialRegex.keys():
                        if instPartialName in inst["name"]:
                            regex = serialRegex[instPartialName]
                    if regex == "":
                        raise Exception("Regular expression not defined for given instrument")
                    serial = re.search(regex, inst["name"]).group()
                    availableSerials.append((serial, serial))

                for neededInst in expReq[instType]:
                    instSerialDropdown = widgets.Dropdown(
                        description=neededInst["purpose"],
                        options=availableSerials
                    )
                    serialDropdownsByType[instType][neededInst["var"]] = instSerialDropdown
                # noinspection PyTypeChecker
                display(widgets.VBox(list(serialDropdownsByType[instType].values())))

        def handle_submitSerials(assignSerialsButton):
            for dropdownInstType in serialDropdownsByType.keys():
                for instNeededVar in serialDropdownsByType[dropdownInstType].keys():
                    serials[instNeededVar] = serialDropdownsByType[dropdownInstType][instNeededVar].value

            doExecAssignment = True
            for singleSerial in serials.values():
                if list(serials.values()).count(singleSerial) > 1:
                    print("\x1b[;43m You cannot pick the same device for more than one purpose \x1b[m ")
                    doExecAssignment = False
                    break
            if doExecAssignment:
                clear_output()
                return assignInstsAndSetupExp(
                    expSetupFunc=expSetupFunc,
                    expReq=expReq,
                    availableInsts=availableInsts,
                    expName=expName,
                    pickedSerials=serials
                )

        assignSerialsBtn = widgets.Button(
            description="Assign Instruments",
            icon="tachometer"
        )
        assignSerialsBtn.on_click(handle_submitSerials)
        display(assignSerialsBtn)

    def assignInstsAndSetupExp(expSetupFunc, expReq, availableInsts, expName, pickedSerials=None):

        if pickedSerials is None:
            pickedSerials = {}
        try:
            if len(pickedSerials.keys()) > 0:
                return expSetupFunc(instruments=availableInsts, serials=pickedSerials, inGui=True)
            else:
                return expSetupFunc(instruments=availableInsts, inGui=True)

        except Exception as errMsg:
            errMsg = str(errMsg).lower()
            if "missing serial" in errMsg:
                getUserSerialAssignment(
                    expSetupFunc=expSetupFunc,
                    expReq=expReq,
                    availableInsts=availableInsts,
                    expName=expName
                )
            elif "connected" in errMsg:
                print('')
                print("All instruments required for", expName)
                for reqInstType in expReq.keys():
                    for inst in expReq[reqInstType]:
                        print("  -", reqInstType, "for", inst['purpose'], "measurement")
                print('')
                reconnectInstructions(inGui=True)
                restartSetupBtn.disabled = False
                restartSetupBtn.on_click(HallPy_Teach)
                # noinspection PyTypeChecker
                display(widgets.VBox([restartSetupBtn]))
            else:
                raise

    def handle_pickExpSubmit(submitBtnAfterClick=None):

        clear_output()
        pickExpDropdown.close = True
        submitBtnAfterClick.close = True
        expSetupFunc = pickExpDropdown.value.setup
        expReq = pickExpDropdown.value.requiredEquipment
        expName = pickExpDropdown.label

        try:
            return assignInstsAndSetupExp(
                expName=expName,
                expSetupFunc=expSetupFunc,
                expReq=expReq,
                availableInsts=instruments
            )
        except Exception as errMsg:
            restartSetupBtn.on_click(HallPy_Teach)
            restartSetupBtn.disabled = False
            print(errMsg)
            # noinspection PyTypeChecker
            display(widgets.VBox([restartSetupBtn]))

    submitBtn.on_click(handle_pickExpSubmit)

"""
HallPy_Teach: A Python package to aid physics students in performing lab activities
===================================================================================

Documentation is available in the docstrings and online at:
https://hallPy.fofandi.dev.

Description
-----------
HallPy_Teach uses the pyvisa package to communicate with lab equipment. It is intended to be
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
from .experiments import curieWeiss, hallEffect
from IPython.core.display import display
from IPython.display import clear_output
import ipywidgets as widgets

from .constants import supportedInstruments, serialRegex
from .helper import reconnectInstructions, getInstTypeCount, filterArrByKey

allExperiments = [
    curieWeiss,
    hallEffect,
]


def initInstruments(inGui: bool = False):
    """Initializing and recognising connected equipment.

    Function does the setup for any of the experiments which use this HallPy_Teach. It recognises the connected
    instruments and provides the instruments in the form of the `inst` object. It also classifies the equipment by their
    uses depending on the manufacturer & model. Equipment is queried using the pyvisa library (`inst.query("*IDN?")`).

    The list of supported instruments is in the constants' module (mentioned in the See Also section).

    Parameters
    ----------
    inGui: bool, default=False
        Bool to check if gui is being used (if using Setup() the whole experiment setup process is done via GUI)

    See Also
    --------
    + constants.supportedEquipment : Used to classify instrument
    + Setup() : Used to use library with GUI in Jupyter Notebook / Lab

    Returns
    -------
    list[object]
        Array of objects containing information about the connected instruments

    Examples
    --------
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


# noinspection PyUnusedLocal
class Setup:
    """Setting up instruments with GUI in jupyter python.

        Class uses initInstruments() and individual experiments setup functions to set up the instruments for performing
        the selected experiment. Subsequently, user will have to use classInstance.expInsts object in the doExpeiment()
        function to perform the given experiment.

        See Also
        --------
        + initInstruments() : Setup class uses this function to find all connected instruments
        + hallEffect.doExperiment() :  Used  after Setup() class initiation - Example doExperiment() function
        + hallEffect.setup() : Used in the Setup() class to set up selected experiment from the GUI

        Notes
        -------
        Use classInstanceName.expInsts in doExperiment() function to perform given experiment.

        Example
        ------
        In jupyter python:

        >>> import HallPy_Teach as Teach
        >>> exp = Teach.Setup()
        >>> data = exp.doExperiment(exp.expInsts)

        Same as doing the following:

        >>> import HallPy_Teach.experiments.hallEffect as Experiment
        >>> import HallPy_Teach as Teach
        >>> insts = Teach.initInstruments()
        >>> expInsts = Experiment.setup(insts)
        >>> data = Experiment.doExperiment(expInsts)
        """

    def __init__(self, btn=None):

        # Getting all experiments in the library
        expChoices = []
        for experiment in allExperiments:
            expChoices.append((experiment.expName, experiment))

        # Setting up UI buttons and dropdowns for later use
        self.restartSetupBtn = widgets.Button(
            description="Restart Setup",
            icon="play",
            disabled=True
        )
        self.pickExpDropdown = widgets.Dropdown(options=expChoices, disabled=False)
        self.submitBtn = widgets.Button(description="Setup Experiment", icon="flask")
        self.submitBtn.on_click(self.handle_pickExpSubmit)

        # Objects and functions to be used after class instance is set up
        self.expInsts = None
        self.doExperiment = None

        clear_output()
        self.instruments = initInstruments(inGui=True)

        # Getting user input for experiment choice
        print(" ")
        print("Choose experiment to perform")

        # noinspection PyTypeChecker
        display(widgets.VBox([self.pickExpDropdown, self.submitBtn]))

    # Getting serial assignment : what instrument is performing what function based on requiredInstruments object
    # defined in the experiment file
    def getUserSerialAssignment(self, expSetupFunc, expReq, availableInsts, expName):
        serials = {}
        serialDropdownsByType = {}
        assignSerialsBtn = widgets.Button(
            description="Assign Instruments",
            icon="tachometer"
        )
        for instType in expReq.keys():
            serialDropdownsByType[instType] = {}
            if len(expReq[instType]) > 1:
                print("Assign", instType + "(s)")
                availableSerials = []
                for inst in filterArrByKey(availableInsts, "type", instType):
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
                self.expInsts = self.assignInstsAndSetupExp(
                    expSetupFunc=expSetupFunc,
                    expReq=expReq,
                    availableInsts=availableInsts,
                    expName=expName,
                    pickedSerials=serials
                )
                return self.expInsts

        assignSerialsBtn.on_click(handle_submitSerials)
        display(assignSerialsBtn)

    # performing the experiment.setup() function for selected experiment.
    def assignInstsAndSetupExp(self, expSetupFunc, expReq, availableInsts, expName, pickedSerials=None):
        if pickedSerials is None:
            pickedSerials = {}

        try:
            # If serials are assigned, setting up experiment instruments with serials
            if len(pickedSerials.keys()) > 0:
                expInsts = expSetupFunc(instruments=availableInsts, serials=pickedSerials, inGui=True)
            else:
                expInsts = expSetupFunc(instruments=availableInsts, inGui=True)

            return expInsts

        except Exception as errMsg:
            errMsg = str(errMsg).lower()
            # if experiment requires multiple of one type of instrument getting serial assignment from user
            if "missing serial" in errMsg:
                self.getUserSerialAssignment(
                    expSetupFunc=expSetupFunc,
                    expReq=expReq,
                    availableInsts=availableInsts,
                    expName=expName
                )

            # Checking if error is for missing required instruments.
            elif "connected" in errMsg:
                print('')
                print("All instruments required for", expName)
                for reqInstType in expReq.keys():
                    for inst in expReq[reqInstType]:
                        print("  -", reqInstType, "for", inst['purpose'], "measurement")
                print('')
                reconnectInstructions(inGui=True)
                self.restartSetupBtn.disabled = False
                self.restartSetupBtn.on_click(Setup)
                # noinspection PyTypeChecker
                display(widgets.VBox([self.restartSetupBtn]))

            # Raising all other errors
            else:
                raise

    # Submit handler after picking experiment.
    def handle_pickExpSubmit(self, submitBtnAfterClick=None):
        clear_output()

        expSetupFunc = self.pickExpDropdown.value.setup
        expReq = self.pickExpDropdown.value.requiredEquipment
        self.doExperiment = self.pickExpDropdown.value.doExperiment
        expName = self.pickExpDropdown.label

        self.pickExpDropdown.close = True
        submitBtnAfterClick.close = True

        try:
            self.expInsts = self.assignInstsAndSetupExp(
                expName=expName,
                expSetupFunc=expSetupFunc,
                expReq=expReq,
                availableInsts=self.instruments
            )
            return self.expInsts
        except Exception as errMsg:
            self.restartSetupBtn.on_click(Setup)
            self.restartSetupBtn.disabled = False
            print(errMsg)
            # noinspection PyTypeChecker
            display(widgets.VBox([self.restartSetupBtn]))

"""
HallPy_Teach: A Python package to aid physics students in performing lab activities
===================================================================================

Documentation is available in the docstrings and online at:
https://hallPy.fofandi.dev.

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

Submodules
----------
+ experiments/

"""

import pyvisa
from IPython.core.display import display
from IPython.display import clear_output
import ipywidgets as widgets

from .experiments import curieWeiss, getAndSetupExpInsts
from .constants import supportedInstruments
from .helper import reconnectInstructions, getInstTypeCount


def initInstruments(inGui=False):
    """Initializing and recognising connected equipment.

    Function does the setup for any of the experiments which use this library. It recognises the connected instruments
    and provides the instruments in the form the `inst` object. It also classifies by their functions depending on
    their manufacturer & model number found by querying the instrument with the pyvisa library
    (`instObj.query("*IDN?")`). The list of supported instruments is in the constants' module.

    See Also
    --------
    constants.supportedEquipment : Used to classify instrument

    Returns
    -------

    """
    rm = pyvisa.ResourceManager()
    res = rm.list_resources()
    instruments = []

    for i in res:
        try:
            # Creating the inst object to be used in the experiments functions (heSetup(), cwSetup(), etc.)
            instResource = rm.open_resource(i)
            name = instResource.query("*IDN?")
            inst = {
                'inst': instResource,
                'name': name,
                'resName': i
            }

            for instrumentType in supportedInstruments.keys():
                for supportedInstrumentName in supportedInstruments[instrumentType]:
                    if supportedInstrumentName in name:
                        inst['type'] = instrumentType

            if len(inst.keys()) == 3:
                inst['type'] = 'Unknown'

            instruments.append(inst)
        except pyvisa.VisaIOError:
            pass
        finally:
            pass

    instTypeCount = getInstTypeCount(instruments)

    if all(instrumentCount == 0 for instrumentCount in instTypeCount.values()):
        print("\x1b[;43m No instruments could be recognised / contacted \x1b[m")
        print('')
        reconnectInstructions(inGui)
        raise Exception("No instruments could be recognised / contacted")
    else:
        countStr = ''
        for instrumentType in instTypeCount.keys():
            if instTypeCount[instrumentType] != 0:
                countStr = countStr + str(instTypeCount[instrumentType]) + " " + instrumentType + "(s)   "

        print(countStr)
        print('')
        reconnectInstructions(inGui)

        return instruments


def HallPy_Teach(btn=None):
    if btn is None:
        btn = {}
    clear_output()
    instruments = initInstruments(inGui=True)

    expChoices = [
        # To Add Hall Effect Later
        # ("Hall Effect Lab", "he"),
        ("Curie Weiss Lab", "cw")
    ]
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
    display(widgets.VBox(onStartWidgets))

    def assignInstsAndSetupExp(expSetupFunc, expReq, availableInsts, expName):

        expInstruments = {}
        try:
            expInstruments = curieWeiss.setup(instruments=availableInsts, inGui=True)
            print("TO-DO")
            print("  - Do experiment guide in GUI or Manual (decided on whats best)")
        except Exception as errMsg:
            errMsg = str(errMsg).lower()
            if "missing serial" in errMsg:
                print('TO-DO')
                print('  - GET SERIALS FROM USER')
            elif "connected" in errMsg:
                clear_output()
                print("\x1b[;41m Required instruments are either not connected or cannot be contacted \x1b[m")
                print("Please connect / reconnect the required instruments from the list below")
                print("Instruments required for", expName)
                for reqInstType in expReq.keys():
                    for inst in expReq[reqInstType]:
                        print("  -", reqInstType, "for", inst['purpose'], "measurement")
                print('')
                reconnectInstructions(inGui=True)
                restartSetupBtn.on_click(HallPy_Teach)
                display(widgets.VBox([restartSetupBtn]))
            else:
                raise

    def handle_pickExpSubmit(submitBtnAfterClick=None):

        clear_output()
        pickExpDropdown.disabled = True
        submitBtnAfterClick.icon = "spinner"
        submitBtnAfterClick.disabled = True
        exp = pickExpDropdown.value
        expName = pickExpDropdown.label

        try:
            if exp == 'cw':
                assignInstsAndSetupExp(
                    expName=expName,
                    expSetupFunc=curieWeiss.setup,
                    expReq=curieWeiss.requiredEquipment,
                    availableInsts=instruments
                )
        except:
            pickExpDropdown.close()
            submitBtn.close()
            restartSetupBtn.on_click(HallPy_Teach)
            display(widgets.VBox([restartSetupBtn]))

    submitBtn.on_click(handle_pickExpSubmit)

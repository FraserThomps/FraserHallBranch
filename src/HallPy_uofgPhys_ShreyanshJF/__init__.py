"""
HallPy_Teach: A Python package to aid physics students in performing lab activities
===================================================================================

Documentation is available in the docstrings and online at:
https://hallPy.fofandi.dev.

Description
-----------
HallPy_Teach uses the pyvisa package to communicate with lab equipment. It is intended to be used as an CAI (Computer
Assisted Instruction) library to let students get setup with labs in a straight forward way. It exposes functions which
can be used to develop any type of computer operated lab if the lab equipment operates on the VISA specificifications
and is supported by pyvisa.

Notes
-----
This library can be used either through the terminal (Command Line) or Jupyter Lab / Notebook. More details can be
found on the online at https://hallPy.fofandi.dev.

Submodules
----------
+ constants.py
+ helper.py
+ experiments.py

"""

import os
import sys
import time
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import clear_output
from IPython.display import Image as ipImage
import asyncio
from .constants import supportedEquipment
from .helper import sortArrByKey, reconnectInstructions


def initInstruments():
    """Initializing and recognising connected equipment.

    Function does the setup for any of the experiments which use this library. It recognises the connected instruments
    and provides the instruments in the form the `inst` object. It also classifies by their functions depending on
    their manufacturer & model number found by querying the instrument with the pyvisa library
    (`instObj.query("*IDN?")`). The list of supported instruments is in the constants module.

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

            for instrumentType in supportedEquipment.keys():
                for i in supportedEquipment[instrumentType]:
                    if i in name:
                        inst['type'] = instrumentType

            if len(inst.keys()) == 3:
                inst['type'] = 'Unknown'

            instruments.append(inst)
        except:
            pass
        finally:
            pass

    instTypeCount = supportedEquipment.copy()

    for instrumentType in instTypeCount:
        instTypeCount[instrumentType] = np.size(sortArrByKey(instruments, 'type', instrumentType))

    instTypeCount['Unknown'] = np.size(sortArrByKey(instruments, 'type', 'Unknown'))

    if all(instrumentCount == 0 for instrumentCount in instTypeCount.values()):
        print("\x1b[;43m No instruments could be recognised / contacted")
        print('')
        reconnectInstructions()
        raise Exception("No instruments could be recognised / contacted")
    else:
        countStr = ''
        for instrumentType in instTypeCount:
            if instTypeCount[instrumentType] != 0:
                countStr = countStr + str(instTypeCount[instrumentType]) + " " + instrumentType + "(s)   "

        print(countStr)
        print('')
        reconnectInstructions()

        return instruments

import time

import numpy as np
from IPython.core.display import clear_output
from pyvisa import VisaIOError

from ..helper import reconnectInstructions, getLCRCap, getLCRCapLoss, showLiveReadings, clearFileAndSaveData
from .__init__ import getAndSetupExpInsts

requiredEquipment = {
    "LCR Meter": [
        {"purpose": "Capacitance", "var": "lcr"}
    ],
    "Multimeter": [
        {"purpose": "Temperature", "var": "mm", "config": ["CONF:TCO", "TCO:TYPE T"]}
    ],
}
"""Required equipment for the Curie Weiss experiment 
"""

expName = "Curie Weiss Lab"
"""Required equipment for the Curie Weiss experiment 
"""


def setup(instruments=None, serials=None, inGui=False):
    """Setup function for the Curie Weiss experiment

        Mainly handles sending proper errors and guidance to students so that they can do a majority of the troubleshooting.
        The actual setup is done by the getAndSetupExpInsts() function.

        Parameters
        ----------
        instruments: list of object
            Array of all the available instruments (see initInstruments() docs for more details)
        serials: object
            Object with key as 'var' name in requiredEquipment and value as the serial number of the specific instrument to be used for the defied purpose
        inGui: bool
            Bool to define if the jupyter python widgets GUI is being used

        Returns
        -------
        object
            Object with keys as the 'var' name set in the requiredEquipment object and values as 'inst' objects (see initInstruments() docs)
        """
    if serials is None:
        serials = {}
    if instruments is None:
        instruments = []

    if len(instruments) == 0:
        print("\x1b[;43m No instruments could be recognised / contacted \x1b[m")
        print("")
        reconnectInstructions(inGui)
        raise Exception("No instruments could be recognised / contacted")

    foundReqInstruments = getAndSetupExpInsts(requiredEquipment, instruments, serials, inGui)

    print("\x1b[;42m Instruments ready to use for Curie Weiss experiment \x1b[m")
    print("Proceed as shown:")
    if inGui:
        print("   1 | cwInstruments = HallPy_Teach()")
        print("   2 | data = placeHolderExperimentFunction(cwInstruments)")
    else:
        print("   1 | cwInstruments = hp.curieWeiss.setup(instruments)")
        print("   2 | data = placeHolderExperimentFunction(cwInstruments)")
    print(' ')
    print("\x1b[;43m NOTE : If any instruments are disconnected or turned off after     \x1b[m")
    print("\x1b[;43m        this point you will have to restart and reconnect them      \x1b[m")
    if inGui:
        print("\x1b[;43m        to the PC and rerun the `HallPy_Tech()` function            \x1b[m")
    else:
        print("\x1b[;43m        to the PC and rerun 'hp.initInstruments()' and              \x1b[m")
        print("\x1b[;43m        hp.curieWeiss.setup()                                       \x1b[m")

    return foundReqInstruments


def exampleExpCode():
    """Prints a demo of how the student should use the doExperiment() function for the Curie Weiss lab

        Returns
        -------
        None
        """
    print("Example: ")
    print("   1 | data = hp.doExperiment(")
    print("   2 |          expInsts=hp.expInsts,")
    print("   3 |          exptLength=50,")
    print("   4 |          measurementInterval=5,")
    print("   5 |          dataFileName='curieWeissData'")
    print("   6 |        )")


def doExperiment(expInsts=None, exptLength=None, measurementInterval=5, dataFileName=None):
    """Function to perform the Curie Weiss experiment

    Parameters
    ----------
    expInsts : object
        Object with keys as the 'var' name set in requiredEquipment object and the value as the 'inst' object of the
        corresponding equipment (see initInstruments() for the 'inst' object)
    exptLength : int
        Length of time the experiment is supposed to run for in minutes.
    measurementInterval : int
        Length of the interval between subsequent mreasurements in seconds
    dataFileName : str, optional
     Name of the file where the collected data will be saved (the saved file will have a '.p' extension)

    Returns
    -------
    dict[str, Union[list, ndarray]]
        Data collected during the experiment. See examples for an example data set

    Example
    -------
    Example data set:

    >>> outputData = {
    >>>     "time": [0, 5, 10, 15, 20, 25, 30],
    >>>     "temp": [24.1, 25.2, 26.4, 27.2, 28.2, 29.2, 30.0],
    >>>     "cap": [2e-9, 3e-9, 4e-9, 5e-9, 6e-9, 7e-9, 8e-9],
    >>>     "capLoss": [2e-11, 2e-11, 2e-11, 2e-11, 2e-11, 2e-11, 2e-11]
    >>> }
    """
    if expInsts is None:
        expInsts = []

    if exptLength is None or type(exptLength) != int:
        exptLength = 0

    inGui = True
    minExpLength = 1
    maxExpLength = 100
    maxMeasurementInterval = 61
    maxOperatingTemp = 61

    if len(expInsts) == 0:
        print("\x1b[;43m No instruments could be recognised / contacted \x1b[m")
        print("")
        reconnectInstructions(inGui)
        raise Exception("No instruments could be recognised / contacted")

    if exptLength < minExpLength or exptLength > maxExpLength:
        print("\x1b[;41m Please provide valid experiment length \x1b[m")
        print("Valid minimum experiment length =", str(minExpLength), " minutes | Valid maximum voltage =",
              str(maxExpLength), "minutes")
        exampleExpCode()
        print("\x1b[;43m NOTE : The desired length should be entered in minutes. (integer values only) \x1b[m")
        raise ValueError("Invalid experiment length value in doExperiment(). Argument in question: expLength")

    if type(measurementInterval) != int or measurementInterval > maxMeasurementInterval:
        print("\x1b[;41m Please provide valid measurement interval time \x1b[m")
        print("Valid maximum measurement interval time =", str(maxMeasurementInterval), "seconds")
        exampleExpCode()
        print("\x1b[;43m NOTE : The desired length should be entered in seconds. (integer values only) \x1b[m")
        raise ValueError("Invalid measurement interval time in doExperiment(). Argument in question: "
                         "measurementInterval")
    data = {
        "time": [],
        "temp": [],
        "cap": [],
        "capLoss": []
    }

    lcr = expInsts["lcr"]["res"]
    mm = expInsts["mm"]["res"]

    timePassed = 0.00
    timeLeft = exptLength * 60

    try:
        while timeLeft > 0:
            startTimeCurLoop = time.time()

            curTemp = float(mm.query("READ?"))
            curCap = getLCRCap(lcr)
            curCapLoss = getLCRCapLoss(lcr)

            data["time"].append(timePassed)
            data["temp"].append(curTemp)
            data["cap"].append(curCap)
            data["capLoss"].append(curCapLoss)

            if dataFileName is not None:
                clearFileAndSaveData(data, dataFileName)

            if curTemp > maxOperatingTemp:
                print("\x1b[;41m IMMEDIATELY TURN OFF THE HEATING ELEMENT \x1b[m")
                print("The temperature has exceeded the maximum operating temperature of", str(maxOperatingTemp), "ºC")
                print("The current temperature is", curTemp, "ºC")
                if dataFileName is not None:
                    print("The data collected till now has been saved in", dataFileName + ".p")

                raise Warning("Temperature exceeded maximum operating temperature")

            liveReadings = {
                "Temp (ºC)": curTemp,
                "Capacitance (F)": curCap,
                "Capacitance Loss (F)": curCapLoss,
                "Time Passed": timePassed,
                "Time Left": timeLeft
            }
            timeVsTempGraph = {
                "title": "Time Vs Temperature",
                "xlim": (-1, (exptLength * 60)),
                "ylim": (np.amin(data["temp"]), np.amax(data["temp"])),
                "xdata": np.array(data["time"]),
                "ydata": np.array(data["temp"]),
                "xlabel": 'Time (S)',
                "ylabel": 'Temperature (ºC)'
            }
            tempVsCapGraph = {
                "title": "Temperature Vs Capacitance",
                "xlim": (np.amin(data["temp"]), np.amax(data["temp"])),
                "ylim": (np.amin(data["cap"]), np.amax(data["cap"])),
                "xdata": np.array(data["temp"]),
                "ydata": np.array(data["cap"]),
                "xlabel": "Temperature (ºC)",
                "ylabel": "Capacitance (F)"
            }

            clear_output(wait=True)
            showLiveReadings(liveReadings=liveReadings, g1=timeVsTempGraph, g2=tempVsCapGraph)
            print("\x1b[;41m The experiment will shut down if the temperature exceeds", str(maxOperatingTemp),
                  "ºC \x1b[m")

            endTimrCurrLoop = time.time()
            loopTime = endTimrCurrLoop - startTimeCurLoop
            if loopTime < measurementInterval:
                time.sleep(measurementInterval - loopTime)

            timePassed += measurementInterval
            timeLeft -= measurementInterval

    except VisaIOError:
        print("\x1b[;41m IMMEDIATELY TURN OFF THE HEATING ELEMENT \x1b[m")
        print("Could not complete the full experiment")
        if dataFileName is not None:
            print("The data collected till now has been saved in", dataFileName + ".p")
        raise
    except:
        print("\x1b[43m Could not complete the full experiment \x1b[m")
        if dataFileName is not None:
            print("The data collected till now has been saved in", dataFileName + ".p")
        raise

    print("Experiment completed")
    if dataFileName is not None:
        print("The data collected till now has been saved in", dataFileName + ".p")

    for key in data.keys():
        if type(data[key]) == list:
            data[key] = np.array(data[key])

    return data

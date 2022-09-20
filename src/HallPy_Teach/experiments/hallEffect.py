import time

import numpy as np
from IPython.core.display import clear_output
from matplotlib import pyplot as plt
from matplotlib.collections import PolyCollection
from pyvisa import VisaIOError

# noinspection
from mpl_toolkits.mplot3d import Axes3D
# Important import even though it is not used

from .__init__ import getAndSetupExpInsts
from ..helper import parseQueryReading, reconnectInstructions, showLiveReadings, setPSCurr, setPSVolt, clearFileAndSaveData

requiredEquipment = {
    "Power Supply": [
        {"purpose": "Electromagnet", "var": "emPS"},
        {"purpose": "Current Supply", "var": "hcPS"}
    ],
    "Multimeter": [
        {"purpose": "Hall Voltage", "var": "hvMM", "config": ["CONF:VOLT:DC"]},
        {"purpose": "Hall Current", "var": "hcMM", "config": ["CONF:CURR:DC"]}
    ],
}
"""Required equipment for the hall effect experiment 
"""

expName = "Hall Effect Lab"
"""Display name for the Hall Effect experiment
"""


def setup(instruments=None, serials=None, inGui=False):
    """Setup function for the Hall effect experiment

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

    print("\x1b[;42m Instruments ready to use for Hall Effect experiment \x1b[m")
    print("Proceed as shown:")
    if inGui:
        print("   1 | cwInstruments = HallPy_Teach()")
        print("   2 | data = placeHolderExperimentFunction(cwInstruments)")
    else:
        print("   1 | cwInstruments = hp.hallEffect.setup(instruments)")
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
    """Prints a demo of how the student should use the doExperiment() function for the Hall Effect lab

    Returns
    -------
    None
    """
    print("Example: ")
    print("   1 | data = hp.doExperiment(")
    print("   2 |          expInsts=hp.expInsts,")
    print("   3 |          emVolts=[10, 20, 30],")
    print("   4 |          hallSweep=(15, 30),")
    print("   5 |          dataPointsPerSupSweep=30,")
    print("   6 |          measurementInterval=1,")
    print("   7 |        )")


def draw3DHELabGraphs(dataToGraph):
    """Outputs 3D graph

    A 3d graph is generated using matplotlib to represent the collected data in doExperiment() for the Hall effect
    experiment

    Parameters
    ----------
    dataToGraph : object
        Data object from doExperiment() in the hall effect experiment

    Returns
    -------
    None
        Outputs 3D graph in jupyter python output window representing the collected data in doExperiment() in
        the hall effect experiment

    """
    fig = plt.figure(figsize=(7, 7))
    ax = fig.gca(projection='3d')

    toGraphOnX = "supplyCurr"
    toGraphOnY = "hallVolt"

    dataScaling = {
        "time": 1,
        "supplyVolt": 1,
        "supplyCurr": 1000000,
        "hallVolt": 1000,
    }
    dataGraphLabels = {
        "time": "Time (s)",
        "supplyVolt": "Supply Volt. (V)",
        "supplyCurr": "Supply Curr. (\u03bcA)",
        "hallVolt": "Hall Volt. (mV)",
    }

    emVsWithData = []
    for emV in list(dataToGraph.keys()):
        if len(dataToGraph[emV]['time']) > 0:
            emVsWithData.append(emV)

    verts = []
    for emV in emVsWithData:
        if len(dataToGraph[emV]['time']) > 0:
            verts.append(list(zip(np.array(dataToGraph[emV][toGraphOnX]) * dataScaling[toGraphOnX],
                                  np.array(dataToGraph[emV][toGraphOnY]) * dataScaling[toGraphOnY]
                                  )))

    for xySet in verts:
        xySet.insert(len(xySet), (xySet[len(xySet) - 1][0], xySet[0][1]))

    faceColours = plt.get_cmap('bone_r')(np.linspace(0.25, 1, len(emVsWithData)))
    poly = PolyCollection(verts, facecolors=faceColours, alpha=0.75)

    ax.add_collection3d(poly, zs=[float(V) for V in emVsWithData], zdir='y')

    allXVals = []
    allYVals = []
    for emV in emVsWithData:
        allXVals.extend(dataToGraph[emV][toGraphOnX])
        allYVals.extend(dataToGraph[emV][toGraphOnY])

    xMax = np.amax(allXVals) * dataScaling[toGraphOnX]
    xMin = np.amin(allXVals) * dataScaling[toGraphOnX]
    yMax = np.amax(allYVals) * dataScaling[toGraphOnY]
    yMin = np.amin(allYVals) * dataScaling[toGraphOnY]
    ax.set_xlabel(dataGraphLabels[toGraphOnX], fontsize=14, labelpad=10)
    ax.set_zlabel(dataGraphLabels[toGraphOnY], fontsize=14, labelpad=10)
    ax.set_ylabel("EM Volt. (V)", fontsize=14, labelpad=10)
    ax.set_yticks([float(V) for V in emVsWithData])
    ax.azim = -105
    ax.elev = 10
    ax.set(xlim=(xMin, xMax),
           zlim=(yMin, yMax),
           ylim=(np.amin([float(V) for V in emVsWithData]) - 2, np.amax([float(V) for V in emVsWithData]) + 2))
    plt.show()


def doExperiment(expInsts=None, emVolts=None, supVoltSweep=(), dataPointsPerSupSweep=0, measurementInterval=1, dataFileName=None):
    """Function to perform the Hall Effect experiment

    For every emVolt from input the experiment will sweep across the hall bar supply voltages provided in the supVoltSweep
    input. During the data collection the current progress will be displayed in the jupyter python output. For more
    information see the experiment webpage: https://hallpy.fofandi.dev/experiments/hallEffect .


    Parameters
    ----------
    expInsts : object
        Object with keys as the 'var' name set in requieredEquipment object and the value as the 'inst' object of the
        corresponding equipment (see initInstruments() for the 'inst' object)
    emVolts : list of float
        A list of float values which dictate the electromagnet voltage input
    supVoltSweep : tuple[float]
        A tuple of 2 float values between which the function will sweep the input voltage for the hall bar
    dataPointsPerSupSweep : int
        The number of data points collected between the minimum and the maximum value of the hall bar voltage sweep (supVoltSweep)
    measurementInterval : int
        Measurement interval between data collections in seconds
    dataFileName : str, optional
        Name of the file where the collected data will be saved (the saved file will have a '.p' extension)

    Returns
    -------
     dict[str, dict[str, Union[list, int]]]
        Data collected during the experiment. See examples for an example data set

    Example
    --------
    Example of the output data format:

    >>> outputData = {
    >>>     '5.0': {
    >>>         "time": [0, 1, 2, 3, 4, 5],
    >>>         "supplyVolt": [0, 1, 2, 3, 4, 5],
    >>>         "supplyCurr": [0, 1e-5, 2e-5, 3e-5, 4e-5, 5e-5],
    >>>         "hallVolt": [0, 0.0005, 0.0007, 0.0008, 0.0010, 0.0015],
    >>>         "emCurr": 0.200
    >>>     }
    >>> }
    """

    if expInsts is None:
        expInsts = []

    if emVolts is None:
        emVolts = []

    inGui = True

    maxEMCurr = 0.700
    maxSupCurr = 0.0001

    if len(expInsts) == 0:
        print("\x1b[;43m No instruments could be recognised / contacted \x1b[m")
        print("")
        reconnectInstructions(inGui)
        raise Exception("No instruments could be recognised / contacted")

    if len(emVolts) == 0 or (type(emVolts) != list and type(emVolts) != np.ndarray):
        print("\x1b[;41m Please provide valid voltage values for the electromagnet \x1b[m")
        print("Valid minimum Voltage = 0.0V | Valid maximum voltage = 30.0V")
        exampleExpCode()
        print("\x1b[;43m NOTE : If you want a constant electromagnet voltage provide a single value list/array. \x1b[m")
        print("(numpy arrays {np.ndarray} are also allowed)")
        print("Example:")
        print("   1 | emVoltage = [15.0]")
        print("This would set the electromagnet voltage to 15.0V for the duration of the experiment.")
        raise ValueError("Invalid electromagnet voltage values in doExperiment(). Argument in question: emVolts")

    for vIndex in range(len(emVolts)):
        try:
            emVolts[vIndex] = float(emVolts[vIndex])
        except ValueError:
            print("\x1b[;41m All provided voltage values for the electromagnet must be numbers \x1b[m")
            print("The following value is the cause of the error :", emVolts[vIndex], "Index number of value :", vIndex)
            raise ValueError("Invalid electromagnet voltage values in doExperiment(). Argument in question: emVolts")

    if len(supVoltSweep) != 2:
        print("\x1b[;43m Please provide a valid sweep range for the supply voltage. \x1b[m")
        print("Valid minimum Voltage = 0.0V | Valid maximum voltage = 30.0V")
        exampleExpCode()
        raise ValueError("Invalid hall bar voltage sweep values in doExperiment(). Argument in question: supVoltSweep")

    if dataPointsPerSupSweep > 100:
        print("\x1b[;41m Please provide a valid number of data points for the current supply sweep. \x1b[m")
        print("Valid minimum data points: 20")
        print("Valid maximum data points: 100")
        print("Current length:", dataPointsPerSupSweep)
        print("\x1b[;43m NOTE : A higher number of either data points or emVolt values can significantly      \x1b[m")
        print("\x1b[;43m        increase the length of the experiment.                                         \x1b[m")
        print("Recommended data points count = 40")
        print("Recommended electromagnet voltage count = 5 | eg.: emVolts=[5, 10, 15, 20, 25]")
        exampleExpCode()
        raise ValueError("Invalid experiment length time in doExperiment(). Argument in question: expLength")

    if measurementInterval < 0.5:
        print("\x1b[;43m Please provide a valid length of time for the experiment to run. \x1b[m")
        print("Valid minimum interval: 0.5 seconds | Valid maximum interval: 5 seconds")
        print("Current interval:", measurementInterval)
        exampleExpCode()
        raise ValueError("Invalid experiment length time in doExperiment(). Argument in question: expLength")

    data = {}
    emVolts.sort()
    for V in emVolts:
        data[str(V)] = {
            "time": [],
            "supplyVolt": [],
            "supplyCurr": [],
            "hallVolt": [],
            "emCurr": 0
        }

    supVoltIncrement = (supVoltSweep[1] - supVoltSweep[0]) / dataPointsPerSupSweep
    if np.absolute(supVoltIncrement) < 0.001:
        print("\x1b[;43m The power supply can only increment the voltage in steps of 0.001V. \x1b[m")
        print("With the current experiment variables the needed voltage increment would be", supVoltIncrement + "V.")
        print("Please do one of the following things to increase the ")
        print("  - Increase the voltage sweep range")
        print("  - Decrease the measurement interval")
        print("  - Increase the experiment length")
        print("For this experiment the voltage increment should ideally be more than 0.05V")
        print("Use the following formula to calculate the voltage increment:")
        print("Voltage Increment = (Max Voltage - Min Voltage) / (Experiment Length (s) / Measurement Interval (s))")
        raise ValueError("Current supply voltage increment would be too low. ")

    if type(dataFileName) is not str and dataFileName is not None:
        print("\x1b[;41m Please provide valid file name for the data to be saved \x1b[m")
        raise TypeError("dataFileName was found to be a " + str(type(dataFileName)) + "when it is supposed to be a "
                                                                                      "string")

    emPS = expInsts["emPS"]["res"]
    hcPS = expInsts["hcPS"]["res"]
    hvMM = expInsts["hvMM"]["res"]
    hcMM = expInsts["hcMM"]["res"]

    setPSCurr(0.700, emPS)
    setPSVolt(0.000, emPS)
    setPSCurr(0.010, hcPS)
    setPSVolt(0.000, hcPS)

    timeBetweenEMVChange = 2.0
    sweepDur = measurementInterval * dataPointsPerSupSweep
    startSupVolt = supVoltSweep[0]
    endSupVolt = (supVoltSweep[1] * 1.01)
    curSupVolt = startSupVolt
    timePassed = 0.000
    timeOnCurSupLoop = 0.000
    timeLeft = float((sweepDur * len(emVolts)) + (timeBetweenEMVChange * (len(emVolts) - 1)))

    try:
        for emV in emVolts:
            setPSVolt(emV, emPS)
            time.sleep(0.6)
            curEMCurr = float(emPS.query("IOUT1?"))
            if curEMCurr > maxEMCurr:
                raise Warning("Electromagnet current was too high. Current before cut off: " + str(curEMCurr))
            data[str(emV)]["emCurr"] = curEMCurr
            curLoopStartTime = time.time()
            while curSupVolt < endSupVolt:
                setPSVolt(curSupVolt, hcPS)
                time.sleep(0.1)
                curSupCurr = parseQueryReading(hcMM.query("READ?"))
                curHallVolt = parseQueryReading(hvMM.query("READ?"))
                if float(curSupCurr) > maxSupCurr:
                    raise Warning("Supply current was too high. Current before cut off: " + str(curSupCurr))

                curLoopEndTime = time.time()
                if (measurementInterval - (curLoopEndTime - curLoopStartTime)) > 0:
                    time.sleep(measurementInterval - (curLoopEndTime - curLoopStartTime))

                data[str(emV)]["time"].append(timeOnCurSupLoop)
                data[str(emV)]["supplyVolt"].append(curSupVolt)
                data[str(emV)]["supplyCurr"].append(curSupCurr)
                data[str(emV)]["hallVolt"].append(curHallVolt)

                if dataFileName is not None:
                    clearFileAndSaveData(data, dataFileName)

                timePassed += measurementInterval
                timeOnCurSupLoop += measurementInterval
                timeLeft -= measurementInterval

                liveReading = {
                    "EM Volt.  (V)": np.round(emV, decimals=3),
                    "EM Curr. (A)": np.round(curEMCurr, decimals=3),
                    "Supply Curr. (\u03bcA)": np.round((curSupCurr * 1000000), decimals=3),
                    "Supply Volt. (V)": np.round(curSupVolt, decimals=3),
                    "Hall Volt. (mV)": np.round((curHallVolt * 1000), decimals=3),
                    "Time on Current EM Volt. (s)": timeOnCurSupLoop,
                    "Time Elapsed (s)": timePassed,
                    "Time Left (s)": timeLeft
                }

                clear_output(wait=True)
                draw3DHELabGraphs(data)
                showLiveReadings(liveReading)

                curSupVolt += supVoltIncrement
                curLoopStartTime = time.time()

            curEMCurr = float(emPS.query("IOUT1?"))
            if float(curEMCurr) > maxEMCurr:
                raise Warning("Electromagnet current is too high. Current before cut off:", str(curEMCurr))

            setPSVolt(0.000, hcPS)
            timeOnCurSupLoop = 0.000
            curSupVolt = startSupVolt
            time.sleep(timeBetweenEMVChange - 0.6)
            timeLeft -= timeBetweenEMVChange

        setPSCurr(0.000, emPS)
        setPSVolt(0.000, emPS)
        setPSCurr(0.000, hcPS)
        setPSVolt(0.000, hcPS)
        print("The power supplies have been reset.")

    except VisaIOError:
        print("\x1b[43m IMMEDIATELY SET ALL THE POWER SUPPLY VOLTAGES TO 0 \x1b[m")
        print("Could not complete the full experiment")
        if dataFileName is not None:
            print("The data collected till now has been saved in", dataFileName + ".p")
        raise
    except:
        setPSCurr(0.000, emPS)
        setPSVolt(0.000, emPS)
        setPSCurr(0.000, hcPS)
        setPSVolt(0.000, hcPS)
        print("The power supplies have been reset.")
        print("\x1b[43m Could not complete the full experiment \x1b[m")
        if dataFileName is not None:
            print("The data collected till now has been saved in", dataFileName + ".p")
        raise

    print("Data collection completed.")
    if dataFileName is not None:
        print("The data collected till now has been saved in", dataFileName + ".p")

    for emV in data.keys():
        for key in data[emV].keys():
            if type(data[emV][key]) is list:
                data[emV][key] = np.array(data[emV][key])

    return data

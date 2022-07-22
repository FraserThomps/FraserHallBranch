import time

import numpy as np
from IPython.core.display import clear_output
from matplotlib import pyplot as plt
from matplotlib.collections import PolyCollection
# Important import
from mpl_toolkits.mplot3d import Axes3D
from pyvisa import VisaIOError

from .__init__ import getAndSetupExpInsts
from ..helper import reconnectInstructions, showLiveReadings, setPSCurr, setPSVolt

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

expName = "Hall Effect Lab"


def setup(instruments=None, serials=None, inGui=False):
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
    print("Example: ")
    print("   1 | data = hp.doExperiment(")
    print("   2 |          expInsts=hp.expInsts,")
    print("   3 |          emVolts=[10, 20, 30],")
    print("   4 |          hallSweep=(15, 30),")
    print("   5 |          dataPointsPerSupSweep=30,")
    print("   5 |          measurementInterval=1,")
    print("   5 |        )")


def draw3DHELabGraphs(dataToGraph):
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
            dataToGraph[emV][toGraphOnX].append(dataToGraph[emV][toGraphOnX][-1])
            dataToGraph[emV][toGraphOnY].append(dataToGraph[emV][toGraphOnY][0])
            verts.append(list(zip(np.array(dataToGraph[emV][toGraphOnX]) * dataScaling[toGraphOnX],
                                  np.array(dataToGraph[emV][toGraphOnY]) * dataScaling[toGraphOnY]
                                  )))

    faceColours = plt.get_cmap('bone_r')(np.linspace(0.25, 1, len(list(dataToGraph.keys()))))
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
    ax.set_ylabel("Electromagnet Volt. (V)", fontsize=14, labelpad=10)
    ax.set_yticks([float(V) for V in emVsWithData])
    ax.azim = -80
    ax.elev = 15
    ax.set(xlim=(xMin, xMax),
           zlim=(yMin, yMax),
           ylim=(np.amin([float(V) for V in emVsWithData]) - 2, np.amax([float(V) for V in emVsWithData]) + 2))
    plt.show()

    del dataToGraph


def doExperiment(expInsts=None, emVolts=None, supVoltSweep=(), dataPointsPerSupSweep=0, measurementInterval=1):
    if expInsts is None:
        expInsts = []

    if emVolts is None:
        emVolts = []

    inGui = True

    maxEMCurr = 0.700
    maxSupCurr = 0.0001

    # TO-D0: Add emergency experiment stop for max current

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
    endSupVolt = supVoltSweep[1]
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
                curSupCurr = float(hcMM.query("READ?"))
                curHallVolt = float(hvMM.query("READ?"))
                if float(curSupCurr) > maxSupCurr:
                    raise Warning("Supply current was too high. Current before cut off: " + str(curSupCurr))

                curLoopEndTime = time.time()
                if (measurementInterval - (curLoopEndTime - curLoopStartTime)) > 0:
                    time.sleep(measurementInterval - (curLoopEndTime - curLoopStartTime))

                data[str(emV)]["time"].append(timeOnCurSupLoop)
                data[str(emV)]["supplyVolt"].append(curSupVolt)
                data[str(emV)]["supplyCurr"].append(curSupCurr)
                data[str(emV)]["hallVolt"].append(curHallVolt)
                timePassed += measurementInterval
                timeOnCurSupLoop += measurementInterval
                timeLeft -= measurementInterval

                liveReading = {
                    "EM Volt.  (V)": np.round(emV, decimals=3),
                    "EM Curr. (I)": np.round(curEMCurr, decimals=3),
                    "Supply Curr. (\u03bcA)": np.round((curSupCurr * 1000000), decimals=3),
                    "Supply Volt. (V)": np.round(curSupVolt, decimals=3),
                    "Hall Volt. (mV)": np.round((curHallVolt * 1000), decimals=3),
                    "Time on Current EM Volt. (s)": timeOnCurSupLoop,
                    "Time Elapsed (s)": timePassed,
                    "Time Left (s)": timeLeft
                }

                dataToGraph = data.copy()
                clear_output(wait=True)
                draw3DHELabGraphs(dataToGraph)
                showLiveReadings(liveReading)

                curSupVolt += supVoltIncrement
                curLoopStartTime = time.time()

            curEMCurr = float(emPS.query("IOUT1?"))
            if float(curEMCurr) > maxEMCurr:
                raise Warning("Electromagnet current is too high. Current before cut off:", str(curEMCurr))

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
        raise
    except:
        setPSCurr(0.000, emPS)
        setPSVolt(0.000, emPS)
        setPSCurr(0.000, hcPS)
        setPSVolt(0.000, hcPS)
        print("The power supplies have been reset.")
        print("\x1b[43m Could not complete the full experiment \x1b[m")
        raise

    print("Data collection completed.")

    for emV in data.keys():
        for key in data[emV].keys():
            if type(data[emV][key]) is list:
                data[emV][key] = np.array(data[emV][key])

    return data

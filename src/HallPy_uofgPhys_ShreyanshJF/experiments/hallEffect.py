import time

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import PolyCollection

from ..helper import reconnectInstructions, clearAndDrawOutputs
from .__init__ import getAndSetupExpInsts

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

    # TO-DO
    # Add live time dependent graph
    fig = plt.figure(figsize=(7, 7))
    ax = fig.gca(projection='3d')

    verts = []
    for Vs in list(dataToGraph.keys()):
        verts.append(list(zip(dataToGraph[Vs][0], dataToGraph[Vs][1])))

    for xySet in verts:
        xySet.insert(0, (xySet[0][0], 0))
        xySet.insert(len(xySet), (xySet[len(xySet) - 1][0], 0))

    faceColours = plt.get_cmap('bone_r')(np.linspace(0.25, 1, len(list(dataToGraph.keys()))))
    poly = PolyCollection(verts, facecolors=faceColours, alpha=0.75)

    ax.add_collection3d(poly, zs=list(dataToGraph.keys()), zdir='y')

    xMax = np.amax(dataToGraph[list(dataToGraph.keys())[-1]][0])
    xMin = np.amin(dataToGraph[list(dataToGraph.keys())[-1]][0])
    yMax = np.amax(dataToGraph[list(dataToGraph.keys())[-1]][1])
    yMin = np.amin(dataToGraph[list(dataToGraph.keys())[-1]][1])
    ax.set_xlabel('Supply Current', fontsize=14, labelpad=10)
    ax.set_zlabel('Hall Voltage', fontsize=14, labelpad=10)
    ax.set_ylabel('Electromagnet Voltage', fontsize=14, labelpad=10)
    ax.set_yticks(list(dataToGraph.keys()))
    ax.azim = -60
    ax.elev = 15
    if len(list(dataToGraph.keys())) <= 2:
        ax.set(xlim=(xMin, xMax), zlim=(yMin, yMax),
               ylim=(np.amin(list(dataToGraph.keys())) - 2, np.amax(list(dataToGraph.keys())) + 2))
    else:
        ax.set(xlim=(xMin, xMax), zlim=(yMin, yMax),
               ylim=(np.amin(list(dataToGraph.keys())), np.amax(list(dataToGraph.keys()))))
    plt.show()


def doExperiment(expInsts=None, emVolts=None, supVoltSweep=(), dataPointsPerSupSweep=0, measurementInterval=1):

    if expInsts is None:
        expInsts = []

    if emVolts is None:
        emVolts = []

    inGui = True

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
    for V in emVolts:
        data[str(V)] = {
            "time": [],
            "supplyVolt": [],
            "supplyCurr": [],
            "hallVolt": []
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

    emPS.write("ISET1:0.700")
    hcPS.write("ISET1:0.010")
    emPS.write("VSET1:0.000")
    hcPS.write("VSET1:0.000")

    timeBetweenEMVChange = 2
    curLoopCount = 0
    sweepDur = measurementInterval * dataPointsPerSupSweep
    expDur = (sweepDur * len(emVolts)) + (timeBetweenEMVChange * (len(emVolts) - 1))
    startEMVolt = emVolts[0]
    startSupVolt = supVoltSweep[0]
    curSupVolt = startEMVolt
    curEMVolt = startSupVolt
    timePassed = 0.000
    timeLeft = expDur
    timeToNextSweep = sweepDur

    # TO-DO
    # Nested while loop
    # Remember to add safety shutoff

    # OLD LOOP
    while curLoopCount != loopMaxCount:
        loopStartTime = time.time()

        if curLoopCount == 0:
            emPS.write("VSET1:" + str(curEMVolt))
            hcPS.write("VSET1:" + str(curSupVolt))
        else:
            if emVoltIncrement != 0:
                curEMVolt = curEMVolt + emVoltIncrement
            curSupVolt = curSupVolt + supVoltIncrement
            emPS.write("VSET1:" + str(curEMVolt))
            hcPS.write("VSET1:" + str(curSupVolt))

        time.sleep(0.1)

        curHallVolt = hvMM.query("READ?")
        curSupI = hcMM.query("READ?")

        liveReadings = {
            'Electromagnet Voltage': curEMVolt,
            'Supply Voltage': curSupVolt,
            'Supply Current': curSupI,
            'Hall Voltage': curHallVolt,
            'Time Elapsed': str(time.strftime("%M:%S", time.gmtime(timePassed))),
            'Time Remaining': str(time.strftime("%M:%S", time.gmtime(timeLeft)))
        }
        clearAndDrawOutputs(liveReadings)

        data["time"].append(timePassed)
        data["emVolt"].append(float(curEMVolt))
        data["supplyVolt"].append(float(curSupVolt))
        data["supplyCurr"].append(float(curSupI))
        data["hallVolt"].append(float(curHallVolt))

        timePassed += measurementInterval
        timeLeft -= measurementInterval
        curLoopCount += 1

        try:
            time.sleep(measurementInterval - (time.time()-loopStartTime))
        except ValueError:
            print("\x1b[;43m Instrument took too long to respond. \x1b[;43m")
            print("This could be because your measurement interval is too short.")
            print("Try increasing your measurement interval to 1 second or more")
            raise Exception("Instrument took too long to respond")
        except:
            raise









    print("Data collection completed.")

    time.sleep(0.2)
    emPS.write("ISET1:0.000")
    hcPS.write("ISET1:0.000")
    emPS.write("VSET1:0.000")
    hcPS.write("VSET1:0.000")

    print("The power supplies have been reset.")

    for key in data.keys():
        data[key] = np.array(data[key])

    return data

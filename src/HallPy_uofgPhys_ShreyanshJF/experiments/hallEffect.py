import time

import numpy as np

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
    print("   3 |          emSweep=(10,30),")
    print("   4 |          hallSweep=(15,30),")
    print("   5 |          expLength=200,")
    print("   5 |          measurementInterval=1,")
    print("   5 |        )")


def doExperiment(expInsts=None, emSweep=(), supVoltSweep=(), expLength=0, measurementInterval=1):

    if expInsts is None:
        expInsts = []

    inGui = True

    # TO-D0: Add emergency experiment stop for max current

    if len(expInsts) == 0:
        print("\x1b[;43m No instruments could be recognised / contacted \x1b[m")
        print("")
        reconnectInstructions(inGui)
        raise Exception("No instruments could be recognised / contacted")

    if len(emSweep) == 0 or len(emSweep) > 2:
        print("\x1b[;43m Please provide a valid sweep range for the electromagnet \x1b[m")
        print("Valid minimum Voltage = 0.0V | Valid maximum voltage = 30.0V")
        exampleExpCode()
        print("\x1b[;41m NOTE : If you want a constant electromagnet voltage provide a single value tuple. \x1b[m")
        print("Example:")
        print("   1 | emVoltage = (15.0)")
        print("This would set the electromagnet voltage to 15.0V for the duration of the experiment.")
        raise ValueError("Invalid electromagnet sweep values in doExperiment(). Argument in question: emSweep")

    if len(supVoltSweep) != 2:
        print("\x1b[;43m Please provide a valid sweep range for the supply voltage. \x1b[m")
        print("Valid minimum Voltage = 0.0V | Valid maximum voltage = 30.0V")
        exampleExpCode()
        raise ValueError("Invalid hall bar voltage sweep values in doExperiment(). Argument in question: supVoltSweep")

    if expLength > 1200:
        print("\x1b[;43m Please provide a valid length of time for the experiment to run. \x1b[m")
        print("Valid minimum experiment duration: 20 seconds")
        print("Valid maximum experiment length: 20 minutes (1200 seconds)")
        print("Current length:", expLength)
        exampleExpCode()
        raise ValueError("Invalid experiment length time in doExperiment(). Argument in question: expLength")

    if measurementInterval < 0.5:
        print("\x1b[;43m Please provide a valid length of time for the experiment to run. \x1b[m")
        print("Valid minimum interval: 0.5 seconds | Valid maximum interval: 5 seconds")
        print("Current interval:", measurementInterval)
        exampleExpCode()
        raise ValueError("Invalid experiment length time in doExperiment(). Argument in question: expLength")

    data = {
        "time": [],
        "emVolt": [],
        "supplyVolt": [],
        "supplyCurr": [],
        "hallVolt": []
    }
    loopMaxCount = expLength / measurementInterval
    supVoltIncrement = (supVoltSweep[1] - supVoltSweep[0]) / loopMaxCount
    emVoltIncrement = 0

    if len(emSweep) != 1:
        emVoltIncrement = (emSweep[1] - emSweep[0]) / loopMaxCount

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

    if 0.001 > np.absolute(emVoltIncrement) > 0:
        print("\x1b[;43m The power supply can only increment the voltage in steps of 0.001V. \x1b[m")
        print("With the given experiment variables the supply voltage increment would be", supVoltIncrement + "V.")
        print("Please do one of the following things to increase the ")
        print("  - Increase the voltage sweep range")
        print("  - Decrease the measurement interval")
        print("  - Increase the experiment length")
        print("For this experiment the voltage increment should ideally be more than 0.05V")
        print("Use the following formula to calculate the voltage increment:")
        print("Voltage Increment = (Max Voltage - Min Voltage) / (Experiment Length (s) / Measurement Interval (s))")
        raise ValueError("Current supply voltage increment would be too low. ")

    emPS = expInsts["emPS"]["inst"]
    hcPS = expInsts["hcPS"]["inst"]
    hvMM = expInsts["hvMM"]["inst"]
    hcMM = expInsts["hcMM"]["inst"]

    emPS.write("ISET1:0.001")
    hcPS.write("ISET1:0.001")
    emPS.write("VSET1:0.000")
    hcPS.write("VSET1:0.000")

    curLoopCount = 0
    startEMVolt = emSweep[0]
    startSupVolt = supVoltSweep[0]
    curSupVolt = startEMVolt
    curEMVolt = startSupVolt
    timePassed = 0.000
    timeLeft = expLength

    while curLoopCount != loopMaxCount:
        loopStartTime = time.time()

        if curLoopCount == 0:
            emPS.write("VSET:" + str(curEMVolt))
            hcPS.write("VSET:" + str(curSupVolt))
        else:
            if emVoltIncrement != 0:
                curEMVolt = curEMVolt + emVoltIncrement
            curSupVolt = curSupVolt + supVoltIncrement
            emPS.write("VSET:" + str(curEMVolt))
            hcPS.write("VSET:" + str(curSupVolt))

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
        data["emVolt"].append(curEMVolt)
        data["supplyVolt"].append(curSupVolt)
        data["supplyCurr"].append(curSupI)
        data["hallVolt"].append(curHallVolt)

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

    return data

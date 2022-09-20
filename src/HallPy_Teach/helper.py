import os
import pickle
import time

import numpy as np
from ipywidgets import widgets
from matplotlib import pyplot as plt
from IPython.display import display

from .constants import supportedInstruments


def parseQueryReading(reading):
    """Helper function parse incoming float values in different formats

        Parameters
        ----------
        reading : string
            String from instrument query

        Returns
        -------
        float
            Returns the first float value found in the string
        """

    try:
        val = float(reading)
        return (val)
    except ValueError:
        try:
            val = reading.split(",")
            return float(val[0])
        except ValueError:
            try:
                val = reading.split(" ")
                return float(val[0])
            except:
                raise
        except:
            raise


def filterArrByKey(arr, key, val):
    """Helper function to find all objects with the same key value in an array of objects

    Parameters
    ----------
    arr : list of object
        List of similar objects to filter from
    key : str
        Key to filter by
    val : any
        Key value to filter for

    Returns
    -------
    list of object
        List of objects where key of given object matches value provided in args

    """
    return list(filter(lambda d: d[str(key)] == val, arr))


def reconnectInstructions(inGui=False):
    """Helper function to display reconnection instructions

    Parameters
    ----------
    inGui : bool, default=False
        To check weather library is being run in the GUI or in Jupyter Python

    Returns
    -------
    None
        Reconnection instructions to output (terminal if not in Jupyter)
    """
    print("\x1b[;43m NOTE : If instruments aren't recognised, follow instructions below: \x1b[m")
    print("  - Disconnect USB / USB hub from PC")
    print("  - Restart kernel (From top menu : Kernel > Restart & Clear Outputs)")
    print("  - Restart Instrument")
    print("  - Connect USB / USB hub to PC")

    if inGui:
        print("  - Press the `Restart Setup` button or rerun the `HallPy_Teach()` function.")
    else:
        print("  - Rerun the `initInstruments()` function.")

    print("*Follow instructions in provided order.")


def getInstTypeCount(instruments):
    """Helper function to get a count instruments by type of instrument

    Parameters
    ----------
    instruments : list of object
        List of instruments objects defined in initInstruments()

    See Also
    --------
    + initInstruments()

    Returns
    -------
    object
        object with key as type of instrument and value as the number of type connected

    """
    instTypeCount = supportedInstruments.copy()

    for instrumentType in instTypeCount:
        instTypeCount[instrumentType] = np.size(filterArrByKey(instruments, 'type', instrumentType))

    instTypeCount['Unknown'] = np.size(filterArrByKey(instruments, 'type', 'Unknown'))

    return instTypeCount


def requiredInstrumentNotFound(instType, inGui=False):
    """Helper function to display information before raising instrument not found error

    Parameters
    ----------
    instType : str
        Type of instrument which is required
    inGui : bool, default=False
        To check weather library is being run in the GUI or in Jupyter Python

    Returns
    -------
    None
        Output to jupyter python or terminal stating required instrument type and other information

    """
    print("\x1b[;41m No " + instType + " is connected. \x1b[m")
    print("Please plug in a " + instType + " via USB to the PC.")
    if inGui:
        print("\x1b[;43m NOTE : You will have to click the `Restart Setup` button or rerun the `HallPy_Teach()` "
              "function after plugging in the " + instType + ". \x1b[m")
    else:
        print("\x1b[;43m NOTE : You will have to rerun the `initInstruments()` function after plugging in the "
              + instType + ". \x1b[m")


def notEnoughReqInstType(instType, requiredEquipment, instruments, inGui=False):
    """Helper function to display information before raising not enough instruments of a single type error

    Parameters
    ----------
    instType : str
        Type of instrument which is in insufficient quantity
    requiredEquipment : object
        Required equipment list from experiment.py file
    instruments : list of object
        List of instrument objects (see initInstruments() docs)
    inGui : bool, default=False
        To check weather library is being run in the GUI or in Jupyter Python

    Returns
    -------
    None
        Output to jupyter python or terminal stating required instrument type and other information

    """
    instTypeCount = getInstTypeCount(instruments)
    if instTypeCount[instType] == 0:
        print("\x1b[;41m No " + instType + " found. \x1b[m")
    else:
        print("\x1b[;41m Only " + str(instTypeCount[instType]) + " " + instType + "(s) found. \x1b[m")
    if len(requiredEquipment[instType]) == 1:
        print(str(len(requiredEquipment[instType])), instType, "is required for this experiment.")
    else:
        print(str(len(requiredEquipment[instType])), instType + "(s) are required for this experiment.")
    print("Please plug the required number of " + instType + "(s) to the PC via USB. ")
    if not inGui:
        print(' ')
        print("\x1b[;43m NOTE : You will have to rerun the `initInstruments()` function after \x1b[m")
        print("\x1b[;43m        plugging in the " + instType + "(s).                          \x1b[m")


# noinspection PyBroadException
def showLiveReadings(liveReadings=None, g1=None, g2=None, g3=None, g4=None):
    """Function to display life readings

    Helper function to display information from a dictionary where the key is the name of the reading and the value is
    the current reading

    Parameters
    ----------
    liveReadings : object
        Object with key as the name of the live reading (eg.: "Voltage") and value as the live reading (eg.: 20.0V)
    g1 : object, optional
        Object with key as matplotlib argument (eg.: title, xlable, xdata) and value of given argument, see notes for
        more information
    g2 : object, optional
        Same as g1
    g3 : object, optional
        Same as g1
    g4 : object, optional
        Same as g1

    Notes
    -----
    Example of liveReadings object:
        {
            'Hall Volt. (V)': 1.00,\n
            'Supply Curr. (mA)': 0.10,\n
            'Time Left (s)': 10\n
        }
    Example g1 object:
        {
            'title':'Some Graph 1',\n
            'xlim': (0,3.16*2),\n
            'ylim': (-1.1,1.1),\n
            'xdata': np.array(range(0, 3145*2, 1))/(curTime+1),\n
            'ydata': np.sin(np.array(range(0, 3145*2, 1))/10),\n
            'xlabel': 'Radians',\n
            'ylabel': 'Sin(Radians)'\n
        }

    Returns
    -------
    None
        Live readings and graphs are printed to jupyter python output

    """
    displayItems = []
    width = 900

    # Checking if graphs need to be shown
    if g1 is not None or g2 is not None or g3 is not None or g4 is not None:
        graphs = [i for i in [g1, g2, g3, g4] if i is not None]
        fig = plt.figure()
        if np.size(graphs) == 1:
            width = 450
            g = graphs[0]
            plt.plot(g['xdata'], g['ydata'])
            plt.grid(True)
            try:
                plt.xlabel(g['xlabel'])
            except:
                pass
            try:
                plt.ylabel(g['ylabel'])
            except:
                pass
            try:
                plt.xlim(g['xlim'])
            except:
                pass
            try:
                plt.ylim(g['ylim'])
            except:
                pass
            try:
                plt.title(g['title'])
            except:
                pass
        elif np.size(graphs) > 1:
            g = []
            if np.size(graphs) == 2:
                fig = plt.figure(figsize=(14, 5))
                g.append(fig.add_subplot(121))
                g.append(fig.add_subplot(122))
            elif np.size(graphs) == 3:
                fig = plt.figure(figsize=(14, 10))
                g.append(fig.add_subplot(221))
                g.append(fig.add_subplot(222))
                g.append(fig.add_subplot(223))
            else:
                fig = plt.figure(figsize=(14, 10))
                g.append(fig.add_subplot(221))
                g.append(fig.add_subplot(222))
                g.append(fig.add_subplot(223))
                g.append(fig.add_subplot(224))
            for i in enumerate(graphs):
                g[i[0]].plot(i[1]['xdata'], i[1]['ydata'])
                g[i[0]].grid(True)
                try:
                    g[i[0]].set_xlabel(i[1]['xlabel'])
                except:
                    pass
                try:
                    g[i[0]].set_ylabel(i[1]['ylabel'])
                except:
                    pass
                try:
                    g[i[0]].set_xlim(i[1]['xlim'])
                except:
                    pass
                try:
                    g[i[0]].set_ylim(i[1]['ylim'])
                except:
                    pass
                try:
                    g[i[0]].set_title(i[1]['title'])
                except:
                    pass
        plt.savefig('tempImg.jpeg')
        plt.close(fig)

    # Checking if live readings need to be shown
    if liveReadings is not None:
        displayItems = []
        for i in liveReadings.keys():
            if 'Time' in i:
                displayItems.append(widgets.VBox([widgets.Label(str(i)), widgets.Label(str(liveReadings[i]))],
                                                 layout=widgets.Layout(
                                                     display="flex",
                                                     justify_content="center",
                                                     align_items="flex-end",
                                                     margin="10px")
                                                 )
                                    )
            else:
                displayItems.append(widgets.VBox([widgets.Label(str(i)), widgets.Label(str(liveReadings[i]))],
                                                 layout=widgets.Layout(
                                                     display="flex",
                                                     justify_content="center",
                                                     align_items="center",
                                                     margin="10px")
                                                 )
                                    )

    # Showing graphs and live readings in correct order
    if liveReadings is not None or g1 is not None or g2 is not None or g3 is not None or g4 is not None:
        finalDisplayStack = []
        if liveReadings is not None:
            finalDisplayStack.append(widgets.HBox(displayItems))
        if g1 is not None or g2 is not None or g3 is not None or g4 is not None:
            _ = widgets.Image(value=open('tempImg.jpeg', 'rb').read(), format='png', width=width)
            finalDisplayStack.append(_)
            os.remove('tempImg.jpeg')

        display(widgets.VBox(finalDisplayStack))


def setPSVolt(volt, inst, channel=1, instSleepTime=0.1):
    """Set Power Supply Voltage

    Function uses pyvisa instrument object to set power supply voltage

    Parameters
    ----------
    volt : int or float
        Voltage value to set
    inst : object
        Power supply Pyvisa Object (value of 'res' in the instrument object in initInstruments())
    channel : int, default=1
        Channel of the power supply which the voltage is to be set to (usually 1 or 2)
    instSleepTime : float, default=0.1
        Time to sleep for inorder to make sure voltage change is applied before carrying on operations

    Returns
    -------
    None

    """
    inst.write("VSET" + str(int(channel)) + ":" + str(volt))
    time.sleep(instSleepTime)


def setPSCurr(curr, inst, channel=1, instSleepTime=0.1):
    """Set Power Supply Current

        Function uses pyvisa instrument object to set power supply current

        Parameters
        ----------
        curr : int or float
            Current value to set
        inst : object
            Power supply Pyvisa Object (value of 'res' in the instrument object in initInstruments())
        channel : int, default=1
            Channel of the power supply which the current is to be set to (usually 1 or 2)
        instSleepTime : float, default=0.1
            Time to sleep for inorder to make sure current change is applied before carrying on operations

        Returns
        -------
        None

        """
    inst.write("ISET" + str(int(channel)) + ":" + str(curr))
    time.sleep(instSleepTime)


def clearFileAndSaveData(data, fileNameWithoutExt):
    """Save data to .p file

    Saves provided data to file in current directory
    Parameters
    ----------
    data: any
    fileNameWithoutExt: str
        File name without extension. It will be saved as a .p file

    Returns
    -------
    None

    See Also
    --------
    + getDataFromFile
    """
    fileName = fileNameWithoutExt + '.p'
    if os.path.exists(fileName):
        os.remove(fileName)
    file = open(fileName, 'wb')

    formattedData = {}

    for key in data.keys():
        if type(data[key]) == list:
            formattedData[key] = np.array(data[key])
        else:
            formattedData[key] = data[key]

    pickle.dump(formattedData, file)


def getDataFromFile(fileNameWithExt):
    """Get data from file

    Gets pickled data from file

    Parameters
    ----------
    fileNameWithExt: str
        Name of file with extension.

    Returns
    -------
    any
        Returns any data within the file

    See Also
    --------
    + saveDataToFile()

    """
    file = open(fileNameWithExt, 'rb')
    dataFromFile = pickle.load(file)
    return dataFromFile


def getLCRCap(inst):
    """Get capacitance reading from provided LCR

    Parameters
    ----------
    inst: object
        LCR PyVisa object (value of 'res' in the instrument object in initInstruments())

    Returns
    -------
    float
        Capacitance as float
    """

    rawMeasurement = inst.query("FETCh?").split(",")  # split from read in
    cap = rawMeasurement[0].strip()  # strip

    if "nF" in cap:
        cap = cap.replace(" nF", "E-9")
    if "pF" in cap:
        cap = cap.replace(" pF", "E-12")
    if "fF" in cap:
        cap = cap.replace(" fF", "E-15")

    return np.float(cap)  # return capacitance


def getLCRCapLoss(inst):
    """Get capacitance loss reading from provided LCR

        Parameters
        ----------
        inst: object
            LCR PyVisa object (value of 'res' in the instrument object in initInstruments())

        Returns
        -------
        float
            Capacitance loss as float
        """
    rawMeasurement = inst.query("FETCh?").split(",")
    capLoss = rawMeasurement[1].strip()

    return np.float(capLoss)

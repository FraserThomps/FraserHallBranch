import os
import time

import numpy as np
from IPython.core.display import clear_output
from ipywidgets import widgets
from matplotlib import pyplot as plt
from IPython.display import display

from .constants import supportedInstruments


# Helper function to find all objects with the same key value in an array of objects
def sortArrByKey(arr, key, val):
    return list(filter(lambda d: d[str(key)] == val, arr))


# Helper function to dispaly reconnection instructions
def reconnectInstructions(inGui=False):
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


# Helper function to get a count instruments by type of instrument
def getInstTypeCount(instruments):
    instTypeCount = supportedInstruments.copy()

    for instrumentType in instTypeCount:
        instTypeCount[instrumentType] = np.size(sortArrByKey(instruments, 'type', instrumentType))

    instTypeCount['Unknown'] = np.size(sortArrByKey(instruments, 'type', 'Unknown'))

    return instTypeCount


# Helper function to display information before raising instrument not found error
def _requiredInstrumentNotFound(instType, inGui=False):
    print("\x1b[;41m No " + instType + " is connected. \x1b[m")
    print("Please plug in a " + instType + " via USB to the PC.")
    if inGui:
        print("\x1b[;43m NOTE : You will have to click the `Restart Setup` button or rerun the `HallPy_Teach()` "
              "function after plugging in the " + instType + ". \x1b[m")
    else:
        print("\x1b[;43m NOTE : You will have to rerun the `initInstruments()` function after plugging in the "
              + instType + ". \x1b[m")


# Helper function to display information before raising not enough instruments of a single type error
def _notEnoughReqInstType(instType, requiredEquipment, instruments, inGui=False):
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


# Helper function to display information from a dictionary where the key is the name of the reading and the value is
# the current reading
def showLiveReadings(liveReadings, g1=0, g2=0, g3=0, g4=0, gTitle='Physics Lab'):
    displayItems = []
    width = 900
    if g1 != 0 or g2 != 0 or g3 != 0 or g4 != 0:
        graphs = [i for i in [g1, g2, g3, g4] if i != 0]
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

    if liveReadings != 0:
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

    if liveReadings != 0 or g1 != 0 or g2 != 0 or g3 != 0 or g4 != 0:
        finalDisplayStack = []
        if liveReadings != 0:
            finalDisplayStack.append(widgets.HBox(displayItems))
        if g1 != 0 or g2 != 0 or g3 != 0 or g4 != 0:
            _ = widgets.Image(value=open('tempImg.jpeg', 'rb').read(), format='png', width=width)
            finalDisplayStack.append(_)
            os.remove('tempImg.jpeg')

        display(widgets.VBox(finalDisplayStack))


def setPSVolt(volt, inst, channel=1, instSleepTime=0.1):
    inst.write("VSET" + str(int(channel)) + ":" + str(volt))
    time.sleep(instSleepTime)


def setPSCurr(volt, inst, channel=1, instSleepTime=0.1):
    inst.write("ISET" + str(int(channel)) + ":" + str(volt))
    time.sleep(instSleepTime)


__all__ = [reconnectInstructions, sortArrByKey]

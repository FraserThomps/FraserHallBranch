def sortArrByKey(arr, key, val):
    return list(filter(lambda d: d[str(key)] == val, arr))


def reconnectInstructions():
    print("\x1b[;43m NOTE : If instruments aren't recognised, follow instructions below \x1b[m")
    print(" - Disconnect USB / USB hub from PC")
    print(" - Restart kernel (From top menu : Kernel > Restart & Clear Outputs)")
    print(" - Connect USB / USB hub to PC")
    print("*Follow instructions in provided order")


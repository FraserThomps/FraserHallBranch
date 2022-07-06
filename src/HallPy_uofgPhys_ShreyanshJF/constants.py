supportedInstruments = {
    "Power Supply": ["TENMA 72-2710", "GDM8324"],
    "LCR Meter": ["B&K Precision ,891"],
    "Multimeter": ["KEITHLEY INSTRUMENTS INC.,MODEL 2110"]
}
"""List of supported instruments sorted by the type of instruments
"""

serialRegex = {
    "TENMA 72-2710": r"SN:[0-9]{8}",
    "B&K Precision ,891": r"[0-9A-Z]{9}",
    "KEITHLEY INSTRUMENTS INC.,MODEL 2110": r"[0-9]{7}"
}
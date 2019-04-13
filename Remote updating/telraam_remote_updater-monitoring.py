import os
import subprocess
import time
import wget

# URL of the update script
UPDATE_URL = "https://telraam-api.net/v0/update-monitoring"
UPDATE_FILE = "/home/pi/Telraam/Scripts/telraam_monitoring.py"

# =================
# MAIN CONTROL LOOP
# =================

try:
    print("Telraam auto-updater: downloading new monitoring file to temporary...")
    TEMP_UPDATE_FILE = UPDATE_FILE + ".updated"
    print("  Downloading from '" + UPDATE_URL + "' to '" + TEMP_UPDATE_FILE + "'...")
    wget.download(UPDATE_URL, TEMP_UPDATE_FILE)

    print("Telraam auto-updater: removing old monitoring file...")
    p = subprocess.call(["sudo", "rm", "-f", UPDATE_FILE])

    print("Telraam auto-updater: renaming new monitoring file...")
    p = subprocess.call(["sudo", "mv", TEMP_UPDATE_FILE, UPDATE_FILE])

except Exception as e:
    print("-> Error while downloading, removing, or renaming monitoring file...")
    print(e)

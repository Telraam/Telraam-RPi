import os
import random
import subprocess
import time
import wget

# predefined time intervals
SERVICE_STARTUP_WAIT_TIME = 3
#UPDATE_PERIOD = 10
UPDATE_PERIOD = 4 * 60 * 60  # Updates are uniformly randomly distributed between 0h00 and 4h00 (= 4 hours * 60 minutes * seconds)
REBOOT_WAIT_TIME = 60

# URL of the update script
UPDATE_URL = "https://telraam-api.net/v0/update"
UPDATE_FILE = "/home/pi/Telraam/Scripts/telraam_remote_updater.py"

# =================
# UTILITY FUNCTIONS
# =================


def is_ap_control_loop_service_running():
    p = subprocess.Popen(["sudo", "systemctl", "status", "telraam_ap_control_loop"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    return "Active: active (running)" in str(out)


def activate_ap_control_loop_service():
    if not is_ap_control_loop_service_running():
        p = subprocess.call(["sudo", "systemctl", "enable", "telraam_ap_control_loop"])
        p = subprocess.call(["sudo", "systemctl", "start", "telraam_ap_control_loop"])
        time.sleep(SERVICE_STARTUP_WAIT_TIME)
        print("AP control loop service activated.")


def deactivate_ap_control_loop_service():
    if is_ap_control_loop_service_running():
        p = subprocess.call(["sudo", "systemctl", "stop", "telraam_ap_control_loop"])
        p = subprocess.call(["sudo", "systemctl", "disable", "telraam_ap_control_loop"])
        time.sleep(SERVICE_STARTUP_WAIT_TIME)
        print("AP control loop service deactivated.")


# =================
# MAIN CONTROL LOOP
# =================

# The script is to be scheduled to run once at 0h00
# It will then halt activation until a random interval has passed (max. 4h)
sleep_time = random.randint(0,UPDATE_PERIOD)
print("Sleeping for " + str(sleep_time) + " seconds...")
time.sleep(sleep_time)

print()
print("Deactivating AP control loop service...");
deactivate_ap_control_loop_service()

print()
try:
    print("Telraam auto-updater: downloading update file...")
    print("  Downloading from '" + UPDATE_URL + "' to '" + UPDATE_FILE + "'...")
    wget.download(UPDATE_URL, UPDATE_FILE)
    print()

    print()
    print("Telraam auto-updater: executing update file '" + UPDATE_FILE + "'...")
    p = subprocess.call(["sudo", "/usr/bin/python3", UPDATE_FILE])

    print()
    print("Telraam auto-updater: removing update file...")
    p = subprocess.call(["sudo", "rm", "-f", UPDATE_FILE])

except Exception as e:
    print("-> Error while downloading, executing, or removing update file...")
    print(e)

print()
print("Activating AP control loop service...");
activate_ap_control_loop_service()

print()
print("Telraam auto-updater: rebooting...")
time.sleep(REBOOT_WAIT_TIME)
p = subprocess.call(["sudo", "/sbin/shutdown", "-r", "now"])

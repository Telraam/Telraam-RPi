import MySQLdb
import socket
import subprocess
import signal
import os
import time

# endpoint for checking internet connection (this is Google's public DNS server)
DNS_HOST = "8.8.8.8"
DNS_PORT = 53
DNS_TIME_OUT = 3

#status constants
STATUS_OK=1
STATUS_NOK=0

# sleep timeintervals
#CONTROL_LOOP_INTERVAL = 20
#CONTROL_LOOP_INTERVAL = 2 * 60
CONTROL_LOOP_INTERVAL = 10 * 60
START_UP_SLEEP_TIME = 15
SERVICE_WAIT_TIME = 3
STARTUP_PERIOD = 100            #after reboot go into AP mode

WPA_SUPPLICANT_HEADER = "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=BE\n"


def is_camera_stream_service_running():
    p = subprocess.Popen(["sudo", "systemctl", "status", "telraam_camera_stream"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    return 'Active: active (running)' in str(out)


def activate_camera_stream_service():
    p = subprocess.call(["sudo", "systemctl", "enable", "telraam_camera_stream"])
    p = subprocess.call(["sudo", "systemctl", "start", "telraam_camera_stream"])
    time.sleep(SERVICE_WAIT_TIME)
    print("Camera stream service activated.")


def deactivate_camera_stream_service():
    p = subprocess.call(["sudo", "systemctl", "stop", "telraam_camera_stream"])
    p = subprocess.call(["sudo", "systemctl", "disable", "telraam_camera_stream"])
    time.sleep(SERVICE_WAIT_TIME)
    print("Camera stream service deactivated.")


def is_monitoring_service_running():
    p = subprocess.Popen(["sudo", "systemctl", "status", "telraam_monitoring"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    return 'Active: active (running)' in str(out)


def activate_monitoring_service():
    p = subprocess.call(["sudo", "systemctl", "enable", "telraam_monitoring"])
    p = subprocess.call(["sudo", "systemctl", "start", "telraam_monitoring"])
    time.sleep(SERVICE_WAIT_TIME)
    print("Monitoring service activated.")


def deactivate_monitoring_service():
    p = subprocess.call(["sudo", "systemctl", "stop", "telraam_monitoring"])
    p = subprocess.call(["sudo", "systemctl", "disable", "telraam_monitoring"])
    time.sleep(SERVICE_WAIT_TIME)
    print("Monitoring service deactivated.")


def run_camera_stream_service():
    if is_monitoring_service_running():
        deactivate_monitoring_service()
    if not is_camera_stream_service_running():
        activate_camera_stream_service()


def run_monitoring_service():
    if is_camera_stream_service_running():
        deactivate_camera_stream_service()
    if not is_monitoring_service_running():
        activate_monitoring_service()


def setup_access_point():
    print("Setting up access point...")
    # reset the config file with a static IP
    # first delete anything that was written after # TELRAAM
    file = open('/etc/dhcpcd.conf', 'r+')
    data = file.readlines()
    pos = 0
    for line in data:
        pos += len(line)
        if line == '# TELRAAM\n':
            file.seek(pos, os.SEEK_SET)
            file.truncate()
        break
    file.close()

    # rewrite the last 3 lines (always after # TELRAAM)
    file = open("/etc/dhcpcd.conf", "a")
    file.write("interface wlan0\n")
    file.write("  static ip_address=192.168.254.1/24\n")
    file.write("  nohook wpa_supplicant")
    file.close()
    p = subprocess.Popen(["sudo", "service", "dhcpcd", "restart"])
    p.communicate()

    # restart the AP
    p = subprocess.Popen(["sudo", "systemctl", "start", "hostapd"])
    p.communicate()

    run_camera_stream_service()
    print("... Pi was reset in AP mode.")
    print()




def check_connection():
    # test the network connection by pinging the predefined (Google's) server
    
    connection_ok = False
    current_time = 0
    while current_time < 20:
        try:
            socket.setdefaulttimeout(DNS_TIME_OUT)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((DNS_HOST, DNS_PORT))
            connection_ok = True
            break
        except Exception:
            current_time += 1
            time.sleep(1)
    
    return connection_ok

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime = float(f.readline().split()[0])
        return uptime
    
    return None

# sleep on start-up
print("Sleeping " + str(round(START_UP_SLEEP_TIME)) + " seconds during startup...")
time.sleep(START_UP_SLEEP_TIME)



connection_ok= check_connection()
uptime=get_uptime()
if(not connection_ok or (uptime and uptime<STARTUP_PERIOD)):
    # at start up pi should be in AP mode
    status = STATUS_NOK
    # enter AP mode if not already active
    p = subprocess.Popen(["sudo", "systemctl", "stop", "hostapd"])
    p.communicate()
    
    setup_access_point()
else:
    run_monitoring_service()
    status = STATUS_OK

# main AP control loop
while True:
    print()
    print("Starting main AP control loop...")

    # the control loop is periodically activated (cf. CONTROL_LOOP_INTERVAL)
    uptime = get_uptime()
    wait_time = CONTROL_LOOP_INTERVAL - uptime%CONTROL_LOOP_INTERVAL
    print("Waiting " + str(round(wait_time)) + " seconds to start main control loop...")
    time.sleep(wait_time)
    print("... Main control loop activated...")

    # connect to Pi's database and retrieve wifi settings
    print()
    print("Checking database for wifi connection information...")
    db = MySQLdb.connect(host="localhost", user="pi", passwd="pi", db="telraam")
    cur = db.cursor()
    cur.execute("SELECT * FROM connection;")
    wifi_ssid = ""
    wifi_pwd = ""
    for row in cur.fetchall():
        wifi_ssid = row[0]
        wifi_pwd = row[1]
        cur.close()
    db.close()

    # check status
    if status == STATUS_OK:
        try:
            connection_ok= check_connection()
            if not connection_ok:
                raise Exception
            print("... Connected to network " + wifi_ssid + "; now sleeping...")
            # already in wifi mode, so do nothing

        except Exception:
            # failed to connect
            status = STATUS_NOK
            print("... Connection to the network failed; updating status...")

            # enter AP mode if not already active
            # check if AP mode is active
            exit_code = 1
            with open(os.devnull, 'wb') as hide_output:
                exit_code = subprocess.Popen(['service', 'hostapd', 'status'], stdout=hide_output, stderr=hide_output).wait()
            if exit_code:
                p = subprocess.Popen(["sudo", "systemctl", "stop", "hostapd"])
                p.communicate()

                setup_access_point()

            else:
                print('... Pi is in AP mode (internal conflict).')
    else:
        if len(wifi_ssid) < 0 or len(wifi_pwd) < 4:
            print("... No valid wifi access codes provided in database.")
            # check if AP is active
            exit_code = 1
            with open(os.devnull, 'wb') as hide_output:
                exit_code = subprocess.Popen(['service', 'hostapd', 'status'], stdout=hide_output, stderr=hide_output).wait()
            if exit_code:
                p = subprocess.Popen(["sudo", "systemctl", "stop", "hostapd"])
                p.communicate()
                file = open("/etc/wpa_supplicant/wpa_supplicant.conf", "w")
                file.write(WPA_SUPPLICANT_HEADER)
                file.close()

                setup_access_point()

            else:
                print('... Pi is in AP mode (internal conflict).')

        else:
            print("... The SSID was found, creating WPA supplicant, stopping hostapd service, starting dhcpcd service...")
            # SSID is new, so replace the conf file
            file = open("/etc/wpa_supplicant/wpa_supplicant.conf", "w")
            file.write(WPA_SUPPLICANT_HEADER)
            file.write("\nnetwork={\n")
            file.write("\tssid=\"" + wifi_ssid + "\"\n")
            file.write("\tpsk=\"" + wifi_pwd + "\"\n")
            file.write("\tscan_ssid=1\n")
            file.write("}")
            file.close()

            # stop the AP
            p = subprocess.Popen(["sudo", "systemctl", "stop", "hostapd"])
            p.communicate()

            # remove the static IP  (last 3 lines of dhcpcd.conf file)
            file = open('/etc/dhcpcd.conf', 'r+')
            data = file.readlines()
            pos = 0
            for line in data:
                pos += len(line)
                if line == '# TELRAAM\n':
                    file.seek(pos, os.SEEK_SET)
                    file.truncate()
                    break
            file.close()

            # restart the wifi
            p = subprocess.Popen(["sudo", "service", "dhcpcd", "restart"])
            p.communicate()

            # wait until the wifi is connected
            wait_time = 10
            print("... Services are restarting, waiting " + str(round(wait_time)) + " seconds...")
            time.sleep(wait_time)
            print("Checking wifi connection...")

            # check connection
            try:
                connection_ok= check_connection()
                if not connection_ok:
                    raise Exception
                print("Connected to " + wifi_ssid + " updating status")
                status = STATUS_OK
                # already in wifi mode, so do nothing

                run_monitoring_service()

            except Exception:
                print("! Error: connection not active.")
                # enter AP mode
                # restart the AP
                p = subprocess.Popen(["sudo", "systemctl", "stop", "hostapd"])
                p.communicate()
                file = open("/etc/wpa_supplicant/wpa_supplicant.conf", "w")
                file.write(WPA_SUPPLICANT_HEADER)
                file.close()

                setup_access_point()


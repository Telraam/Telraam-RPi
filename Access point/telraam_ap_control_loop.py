import socket
import subprocess
import signal
import os
import time
import re
import signal
import requests
import uuid
import json

# endpoint for checking internet connection (this is Google's public DNS server)
DNS_HOST = "8.8.8.8"
DNS_PORT = 53
DNS_TIME_OUT = 3

#status constants
STATUS_OK=1
STATUS_NOK=0

# sleep timeintervals
#CONTROL_LOOP_INTERVAL = 20
#CONTROL_LOOP_INTERVAL = 1 * 60
CONTROL_LOOP_INTERVAL = 10 * 60
START_UP_SLEEP_TIME = 15
SERVICE_WAIT_TIME = 3
STARTUP_PERIOD = 100            #after reboot go into AP mode

#wifi credentials file
WIFI_CREDENTIALS_FILE='/home/pi/Telraam/Scripts/json/telraam_wifi.json'

#stop hotspot from being active after 3 times
STOP_HOTSPOT_MAX=3
HOTSPOT_COUNTER=0

#var and function for the interrupt from php
BREAK_LOOP=False
def signal_received(signal_number, frame):
    global BREAK_LOOP
    BREAK_LOOP=True

    print('Interrupt received!')
signal.signal(signal.SIGUSR1, signal_received)    


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

def activate_dnsmasq_service():
    p = subprocess.call(["sudo", "systemctl", "enable", "dnsmasq"])
    p = subprocess.call(["sudo", "systemctl", "start", "dnsmasq"])
    time.sleep(SERVICE_WAIT_TIME)
    print("Dnsmasq service activated.")


def deactivate_dnsmasq_service():
    p = subprocess.call(["sudo", "systemctl", "stop", "dnsmasq"])
    p = subprocess.call(["sudo", "systemctl", "disable", "dnsmasq"])
    time.sleep(SERVICE_WAIT_TIME)
    print("Dnsmasq service deactivated.")


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
    
    global HOTSPOT_COUNTER
    print('setup_access_point HOTSPOT_COUNTER: {counter}'.format(counter=HOTSPOT_COUNTER))
    HOTSPOT_COUNTER+=1
    
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

    activate_dnsmasq_service()

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

def stop_access_point():
	print("Stopping access point...")

	p = subprocess.Popen(["sudo", "systemctl", "stop", "hostapd"])
	p.communicate()

def check_connection():
    # test the network connection by pinging the predefined (Google's) server
    
    print('Checking wifi connection')
    
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
    
    print('connection_ok: {}'.format(connection_ok))
    
    return connection_ok

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime = float(f.readline().split()[0])
        return uptime
    
    return None

def get_wifi_credentials():
    print('Getting wifi credentials from file')
    
    try:
        with open(WIFI_CREDENTIALS_FILE) as wifi_file:
            data=json.load(wifi_file)
            # print(data)
            return data['wifi_ssid'], data['wifi_pwd']
    except FileNotFoundError as e:
        print('FileNotFoundError:\n{}'.format(e))
    return '', ''

def get_wifi_bssid(ssid):
    print('... Getting wifi bssid for ssid={}'.format(ssid))

    ap_list=[]
    out_newlines=None

    for i in range(5):              #try max 5 times
        print('\ttrying... {}'.format(i))
    
        scan_cmd='sudo iw dev wlan0 scan ap-force'
        process = subprocess.Popen([scan_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        
        if(len(err)==0):                                                #the command did not produce an error so e can process the list of access points
            out_newlines=str(out).replace('\\n', '\n')                  #because of the bytes to str conversion newlines are \\n instead of \n
            
            break
        else:
            print('\terror: {}'.format(err))

        time.sleep(2)                                                   #sleep before retrying
        
    if(not out_newlines):                                               #the command produced an error every time, return no bssid
        return None
        
    split_str=re.findall('BSS.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*SSID.*\n', out_newlines, re.MULTILINE)

    for cell in split_str:     
        ap={}
        ap['bssid']=None
        ap['frequency']=None
        ap['signal']=None
        ap['ssid']=None
        
        m=re.search('BSS\s*([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})', cell)
        if(m):
            ap['bssid']=m.group(1)

        m=re.search('freq:\s*(\d+)', cell)
        if(m):
            ap['frequency']=int(m.group(1))
        
        m=re.search('signal:\s*(-?\d+\.\d+)\s*dBm', cell)
        if(m):
            ap['signal']=float(m.group(1))
        
        m=re.search('SSID:\s*(.+)', cell)
        if(m):
            ap['ssid']=m.group(1)
        
        ap_list.append(ap)

    ap_list=[x for x in ap_list if x['ssid']==ssid]                     #filter for ssid
    
    print('Access points found for ssid={}:'.format(ssid))
    for ap in ap_list:
        print(ap)
    
    ap_list=[x for x in ap_list if x['frequency']<2500]                 #filter for 2.4 GHz wifi band -> freqs lower than 2500 MHz
    ap_list=sorted(ap_list, key=lambda x: x['signal'], reverse=True)    #sort on signal_level
    
    if(len(ap_list)>0):
        print('Using access point: {}'.format(ap_list[0]))
        return ap_list[0]['bssid']
    else:
        print('Did not find any access points')
        return None

def send_online_ping():
    print('send_online_ping')
    url='http://telraam-api.net/v1/private/online'
    token='4M2u0kLC2WPL7oLMA4NC1yWevHJilMz2MGnQym00'
    headers={'Content-Type': "application/json", 'X-Api-Key': token}
    
    data={
        "mac": uuid.getnode()
    }
    
    for i in range(5):              #try 5 times max
        try:
            ret = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
            
            if ret.status_code==200:
                print('ping sent')
                break
            else:
                print('retrying, status code={}'.format(ret.status_code))
        except Exception as e:
            print('exception when posting to url:{}'.format(e))
        
        
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
    deactivate_dnsmasq_service()
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
    for i in range(int(wait_time)+1):
        time.sleep(1)
        
        if(BREAK_LOOP):
            print('Breaking the wait loop')
            BREAK_LOOP=False
            break
    
    print("... Main control loop activated...")

    wifi_ssid, wifi_pwd=get_wifi_credentials()

    # check status
    connection_ok= check_connection()
    if connection_ok:
        print("... Connected to network " + wifi_ssid + "; now sleeping...")
        # already in wifi mode, so do nothing
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
                file.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=BE\n")
                file.close()

                if(HOTSPOT_COUNTER>=STOP_HOTSPOT_MAX):
                	stop_access_point()
                else:
                	setup_access_point()

            else:
                print('... Pi is in AP mode (internal conflict).')
                
                print('internal conflict HOTSPOT_COUNTER: {counter}'.format(counter=HOTSPOT_COUNTER))
                
                if(HOTSPOT_COUNTER>=STOP_HOTSPOT_MAX):
                	stop_access_point()
                
                HOTSPOT_COUNTER+=1
                

        else:
            print("... The SSID was found, creating WPA supplicant, stopping hostapd service, starting dhcpcd service...")
            
            wifi_bssid=get_wifi_bssid(wifi_ssid)
            
            # SSID is new, so replace the conf file
            file = open("/etc/wpa_supplicant/wpa_supplicant.conf", "w")
            file.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=BE\n")
            file.write("\nnetwork={\n")
            if(not wifi_bssid): 
                file.write("\tssid=\"" + wifi_ssid + "\"\n")
            else:
                file.write("\tbssid=" + wifi_bssid + "\n")
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

            # check connection
            try:
                connection_ok= check_connection()
                if not connection_ok:
                    raise Exception
                
                print("Connected to " + wifi_ssid + " updating status")
                status = STATUS_OK
                # already in wifi mode, so do nothing

                deactivate_dnsmasq_service()
                send_online_ping()
                run_monitoring_service()

            except Exception:
                print("! Error: connection not active.")
                # enter AP mode
                # restart the AP
                p = subprocess.Popen(["sudo", "systemctl", "stop", "hostapd"])
                p.communicate()
                file = open("/etc/wpa_supplicant/wpa_supplicant.conf", "w")
                file.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=BE\n")
                file.close()

                if(HOTSPOT_COUNTER>=STOP_HOTSPOT_MAX):
                	stop_access_point()
                else:
                	setup_access_point()



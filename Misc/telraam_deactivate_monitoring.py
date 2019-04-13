import socket
import subprocess
import signal
import os
import time

# sleep timeintervals
SERVICE_WAIT_TIME = 3


def is_camera_stream_service_running():
    p = subprocess.Popen(["sudo", "systemctl", "status", "telraam_camera_stream"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    return 'Active: active (running)' in str(out)


def activate_camera_stream_service():
    p = subprocess.call(["sudo", "systemctl", "enable", "telraam_camera_stream"])
    p = subprocess.call(["sudo", "systemctl", "start", "telraam_camera_stream"])
    time.sleep(SERVICE_WAIT_TIME)
    print("Camera stream service activated.");


def deactivate_camera_stream_service():
    p = subprocess.call(["sudo", "systemctl", "stop", "telraam_camera_stream"])
    p = subprocess.call(["sudo", "systemctl", "disable", "telraam_camera_stream"])
    time.sleep(SERVICE_WAIT_TIME)
    print("Camera stream service deactivated.");


def is_monitoring_service_running():
    p = subprocess.Popen(["sudo", "systemctl", "status", "telraam_monitoring"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    return 'Active: active (running)' in str(out)


def activate_monitoring_service():
    p = subprocess.call(["sudo", "systemctl", "enable", "telraam_monitoring"])
    p = subprocess.call(["sudo", "systemctl", "start", "telraam_monitoring"])
    time.sleep(SERVICE_WAIT_TIME)
    print("Monitoring service activated.");


def deactivate_monitoring_service():
    p = subprocess.call(["sudo", "systemctl", "stop", "telraam_monitoring"])
    p = subprocess.call(["sudo", "systemctl", "disable", "telraam_monitoring"])
    time.sleep(SERVICE_WAIT_TIME)
    print("Monitoring service deactivated.");


deactivate_monitoring_service()

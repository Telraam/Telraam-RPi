#!/usr/bin/env python

import os
import time


def get_temperature():
    temperature = os.popen("vcgencmd measure_temp").readline()
    return (temperature.replace("temp=",""))


while True:
    print("Current temperature is " + get_temperature())
    time.sleep(0.5)

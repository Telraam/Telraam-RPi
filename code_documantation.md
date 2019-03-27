# Telraam.py documentation

Our goal is to detect moving objects (pedestrians, bikers, cars, and trucks) in a live video feed using python and the [OpenCV library](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_tutorials.html). We are using a [Raspberry Pi 3 Model B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/) or a [3A+](https://www.raspberrypi.org/products/raspberry-pi-3-model-a-plus/) (same but 512 MB memory instead of 1GB, but we are using less than 300 MB) and the [Raspberry Pi Camera Module v2](https://www.raspberrypi.org/products/camera-module-v2/), that we are planning to run in a 720p resolution at the possible highest FPS (this will actually be limited by the processing speed of the script, not the camera hardware). 

#### Running the script

To run the current test version of the script with all testing options enabled:

```
sudo modprobe bcm2835-v4l2
```
```
python3 Telraam.py --test --display --idandtrack --rotate 180
```

Skip --test --display --idandtrack if you just want it without display and test data, use --fov alone if you just want to set the field of view, and --rotate 180 if camera is installed upside down)

## Sketch of the script

The script builds around a cycle of **1) Background calibration** – **2) Object (contour) detection** – **3) Data transfer**. Most often data transfer is followed by measuring (object detection) again, except when too much time has passed since the last background measurement, when a new background is calculated before proceeding with object detection. There is a step **4) Object tracking**, which should happen either between steps 2) and 3) or off-site from the contour data provided by step 2) and transferred to the server in step 3) - this is how currently it is implemented on the active Telraam network. This step has the task of identifying individual objects from the large set of contours, and tracking them across the frame. **5) Object classification** happens on the server side, it is based on basic clustering principles, and it has the task of deciding if one object was a pedestrian, a cyclist, a car, or a larger motorized vehicle. This part is not discussed any further here.

These main parts have their own challenges, but a major guideline is that we try to keep everything as simple as possible that needs to run on the Raspberry Pi real-time, as frame-rate seems to be a bottleneck at this time. (With no displays enabled, we are running at around 30 FPS).

## 1) Background calibration

## 2) Object (contour) detection

## 3) Data transfer

## 4) Object tracking

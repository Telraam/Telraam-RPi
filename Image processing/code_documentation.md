# telraam_monitoring.py documentation

Our goal is to detect moving objects (pedestrians, bikers, cars, and trucks) in a live video feed using python and the [OpenCV library](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_tutorials.html). We are using a [Raspberry Pi 3 Model B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/) or a [3A+](https://www.raspberrypi.org/products/raspberry-pi-3-model-a-plus/) (same but 512 MB memory instead of 1GB, but we are using less than 300 MB) and the [Raspberry Pi Camera Module v2](https://www.raspberrypi.org/products/camera-module-v2/), that we are planning to run in a 720p resolution at the possible highest FPS (this will actually be limited by the processing speed of the script, not the camera hardware). 

#### Running the script

**To run the current test version of the script with all testing options enabled:**

```
sudo modprobe bcm2835-v4l2
python3 telraam_monitoring.py --test --display --idandtrack
```

The first command is needed in order to enable directly access the camera using openCV instead of using a slower Python library. Skip --test --display --idandtrack if you just want it without display and test data, use --fov alone if you just want to set the field of view, and --rotate 180 if the camera is not installed upside down. Keep in mind that --display has a huge hit on the frame rate, so only use that for specific testing.)

**When you decide to make a test-setup, please consult the [camera placement notes](./camera_placement_notes.md)** first!

## Sketch of the script

The script builds around a cycle of **[1) Background calibration](https://github.com/Telraam/Telraam-RPi/blob/master/code_documantation.md#1-background-calibration)** – **[2) Object (contour) detection](https://github.com/Telraam/Telraam-RPi/blob/master/code_documantation.md#2-object-contour-detection)** – **[3) Data transfer](https://github.com/Telraam/Telraam-RPi/blob/master/code_documantation.md#3-data-transfer)**. Most often data transfer is followed by measuring (object detection) again, except when too much time has passed since the last background measurement, when a new background is calculated before proceeding with object detection. There is a step **[4) Object tracking](https://github.com/Telraam/Telraam-RPi/blob/master/code_documantation.md#4-object-tracking)**, which should happen either between steps 2) and 3) or off-site from the contour data provided by step 2) and transferred to the server in step 3) - this is how currently it is implemented on the active Telraam network. This step has the task of identifying individual objects from the large set of contours, and tracking them across the frame. **5) Object classification** happens on the server side, it is based on basic clustering principles, and it has the task of deciding if one object was a pedestrian, a cyclist, a car, or a larger motorised vehicle. This part is not discussed any further here.

These main parts have their own challenges, but a major guideline is that we try to keep everything as simple as possible that needs to run on the Raspberry Pi real-time, as frame rate seems to be a bottleneck at this time. With no displays enabled, we are running at around 30 FPS.

### 1) Background calibration

**Goal:** The first task is deriving a background image, that we can use as reference afterwards.

**Implementation:** This part simply collects a set of frames and then calculates the median of them. How often (minimum and preferably) and for how long this runs is specified by parameters (e.g., every 5-6 minutes and for 1 minute, or every 2.5-3 minutes for 30 seconds – latter seems to handle better light/shadow areas moving across the frame on clear days). Before each background calibration a small function sets the exposure time (and fixes all camera settings manually), so camera settings are consistent during background calculations. Light levels can change during background calculation cycles, this is taken into account in step 2) with a flexible threshold level. If the light levels are insufficiently low (or too high – which is unlikely to happen), the loop pauses for 5 minutes then retries (and an empty data stream also happens to still communicate to the server that the camera is up and running.)

**Notes:** OpenCV has background detection methods that do not need the calculation of a global background frame (instead they work from frame-by-frame differences, etc.), but they are an order of magnitude slower, and the results provided are not significantly better (e.g., it has issues with objects that slow down, stop, then start moving again: in the stopped phase these are not properly detected) – although the speed bottleneck is the main reason against using them. 

It would be also an option to do without a dedicated background calculation interval to have an image buffer (that contains the last minute of images) and always calculate the median of this as background, but moving the frames always into a 3D image array takes up way too much resources, which again means that we cannot seem to be able to do this.

We also experimented with using frame-by-frame differences, but the situation there is even further from universal, so we decided against following this direction. Main issues with frame-by-frame tracking are the following: slowly moving objects (pedestrians further away from the camera, or slowly-rolling cars in high traffic situation) are not picked up properly or at all, therefore tracking these object becomes impossible. One object creates a complex structure of shapes in the frame-by-frame differential images, which creates a much more complex tracking and identification problem (meaning multiple shapes will make up one object, and these shapes might not even be close to each other, as the leading and trailing edge of a truck will create two shapes, but in between there will be no difference as the side of the truck has the same colour, so shifting it left or right does not make a difference on the level of given pixels).

**Current challenges:** there is still the issue that in situations where long standstills can occur in traffic (even in non-congested situations as, e.g., the traffic light in one direction is longer red than green), which mean that the median background can sometimes include the image of one or several stopped vehicles. These ghost-objects result in stationary ghost-detections that will significantly worsen the situation by merging any two objects that touch them at the same time, and by separating one object into possibly multiple objects (which can still be solved in post processing). The biggest issue is that when many of these ghost-objects are detected in the field of view, that can lead to actual objects being constantly merged with these ghost-contours as they move across the frame. This might mean that all the time only one object contour is detected that contains maybe no, but maybe multiple objects. This is an issue that cannot be solved in the post processing stage. An additional issue is that this can occur anywhere in congested situations, especially when the flow is really slow and distance between cars is minimal (this leads to the background surface not being visible for more than 50% of the time). The only solution to these problems would be somehow knowing which pixels are background and which are not already during the background calculation, but this seems to be a very difficult nut to crack. In practice, this only presents as a complication at a limited number of cases (if the traffic flow is not continuous enough; e.g., streets with congestion, or cameras placed very close to traffic lights).

### 2) Object (contour) detection

**Goal:** The second task is to identify areas in the background-subtracted image that contain (possible) objects.

**Implementation:** The main idea of the implementation is very simple: by applying a threshold on the background-subtracted image, we define a binary image where pixels are either objects (1) or not (0). Then on this binary image we perform a contour-detection, and then take all top level contours as object candidates.

For these contours many parameters are saved (such as centroid positions, area, width, and height).

**Notes:** Before the threshold is applied, some minor transformations are preformed; mainly we apply a small Gaussian blur to filter out noise, and smoothen detected shapes which both result in a better, more precise, and faster contour detection later.

We experimented using opening and closing instead of the blur, but these are all frame-rate killers (as they take much more time to calculate), so we really cannot do that. Even using a simple square 10x10 kernel, the speed would be half compared to a simple blurring algorithm.

The applied threshold is dynamic, and it depends on the histogram of the background-subtracted image. This is necessary because between background calculations the overall brightness of the scenery will most often change (due to many variables, e.g., the light levels changing simply because the sun gets higher/lower, clouds roll over, etc.), therefore overall the deviation from an earlier background will not be constant even if there is no change in the scenery at all. For example, if the overall luminance of the field grows, then the background-subtracted image will not be all zeros, but for example all tens or more. As the deviation grows larger, larger parts of the image would be pushed above a fixed threshold. This is circumvented in this script by fixing the threshold to be a given (parameter-controlled) value over the ever-changing level in the histogram under which 50% of all pixel count can be found. This 50% will be dominated by the values of the actual non-changed but maybe brightened or darkened background pixels of the background-subtracted image. This region will not really be influenced by objects crossing the screen as their pixels will be typically much brighter on the differential image, and since objects have various shades of colors over them, these pixels will not cluster around a given intensity value as much either as the values corresponding to the background. (This might sound complicated, but running the script in --display mode this is also visualised.)

**Current challenges:** It is more in the data processing part, but let us note it here: detecting contours themselves is not really a challenge. But it happens that one object is detected as multiple contours (for example people can wear coats or sweaters that have the same luminance as the background, so their feet and head will be a different blob), or multiple objects can be recorded as one contour (in case of merging, overlaps, etc). These need to be handled in post processing. When one object is visible as two separated by a small distance should be easy to handle, but for example when there is a continuous overlap during the whole visibility of multiple objects, there we will not able to detect them as multiple objects with a simple solution. In small traffic streets therefore we expect to have nearly no issues, but in high traffic streets with multiple lanes simultaneously occupied in the field of view there will be issues. Long shadow/light borders sweeping through the frame can also influence object sizes and can cause more frequent merging, but right now we have no way of avoiding this.

### 3) Data transfer

**Goal:** Transfer data to the server. 

**Implementation:** Simply when a given amount of time (a preferred time if frame of view empty, or a maximum time if there is constant traffic in the frame) has elapsed between two data dumps, or it is time for a new background calculation, we transfer the data. Since contours are continuously collected in a numpy array, data transfer here is as easy as sending that array through to the server (for the raw data, and sending a processed output with the actual object data).

**Notes:** We send some data (Telraam ID - derived from the MAC address of the wifi chip on the RPi -, timestamp, and all zeros elsewhere) even if there were no contours/objects observed, or if there is no active observing going on because it is too dark/bright (then last record is -1 or -2 to differentiate from no objects observed when it is 0) outside (latter never happens) so the server knows that a given Telraam is still working.

Because of the background calculation loops, some part of the cycle is not spent observing, so this somehow needs to be corrected for if we need to get the actual traffic volumes (e.g. a 30 sec background calculation cycle and 2.5 minutes recording – assuming that data transfer is more or less instantaneous – means that 1/6th of the total time is not actual observing time, therefore volumes should be taken at ~120% observed). For this reason we save the beginning and the end of the observing times, and from this it can be calculated how much time in the 1 hour windows that are shown on the Terlaam site was downtime. This information is also sent to the database (MAC address, start time, end time, status code).

If the wifi connection of the user or the server goes down, the telraam will still keep observing and store the not yet transferred data in a buffer, so there is no extra downtime introduced by loss of connection. If the data to be transferred is too large, it is broken into smaller packets and transferred in pieces.

As ID we use the decimal version of the MAC address of the wifi chip of the RPi. These are globally unique.

The following properties are transferred per contour: MAC address, time of the observation (UNIX seconds), x coordinate, y coordinate, size, width, height.

**Current challenges:** If we also transfer raw contour data, there is a too big load on the server. Storing raw contour data is useful because it enables reprocessing of the data in the future with, e.g., a better tracking algorithm, but it also means approximately two orders of magnitudes more data... For now, transfer of the raw contour data is commented out, but we would like to reenable this in the future.

### 4) Object tracking

**Goal:** The goal is identifying individual objects from a large set of contour time series, possibly handle overlaps (where multiple objects are detected as one single contour) and segmented objects (where one object is detected as multiple smaller contours). The two latter are not implemented yet.

**Implementation:** Right now this step is implemented on the RPi, but we need a) a more sophisticated method, b) consider moving it to the server side. 

What right now is available is an algorithm based on (but extended with extra features) the main ideas presented [here](http://jorgemoreno.xyz/pycvtraffic.php)

The main loop is the following:
1. Let’s assume we detect one object on the first frame. This is given an ID, and we save its properties into a dataframe. When we process the next frame, let’s assume we find two contours. For each of these we check if they are within a threshold to any object on the previous frame (we require that an object’s movement from the previous frame is maximum half the object’s larger axis – as small objects usually move slower), if yes, then we know we have found the same object on this frame, so it gets the same ID, if not, this is a new object with a new ID., etc.
2. For each frame that contains objects we save the properties of each object under the corresponding ID.
3. For the final data that would be transferred to the server we calculate average properties of each object, plus add the starting time, interval, and number of frames observed for each of them. To decide if an observed object is real or is a result of some artefact (moving leaves, shadows, etc.) we require that real objects have a trajectory (the difference between the two furthest observed centroid locations) of at least half the vertical image dimension (which helps filtering out waving trees, moving shadows or light spots reflected from windows, etc.). (On the server there are furthere tests.)

**Notes:** The following properties are saved per object: MAC address, time of the first observation, average x coordinate, average y coordinate, average speed in x, average speed in y, average size, average horizontal size, average vertical size, trajectory length, duration of observations, number of frames being observed for given object.

**Current challenges:** We need to include some sort of Bayesian tracking, where functions describe probabilities, objects need to be added, tracked, and removed from the frame, etc. The current version will fail in busy situations where overlaps are frequent.


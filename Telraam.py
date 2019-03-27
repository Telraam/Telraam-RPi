# TELRAAM monitoring script by Dr. Péter I. Pápics (Transport & Mobility Leuven)
#
# Version history:
# v0024: (P. Papics) commented out lines 524-534 to temporarily disable the transfer of raw contour data to the server
# v0023: (S. Maerivoet) changed access point for the API calls to telraam-api.net
# v0022: (S. Maerivoet) changed cloudfront API calls to https protocol
# v0021: (S. Maerivoet) fixed some types + (W. Himpe) fixed sending data to the back-end using JSON
# v0020: (W. Himpe) changed the back-end URLs + (P. Papics) removed the quotes around numbers when storing them to the back-end them using JSON
# v0019: (S. Maerivoet) code validated according to PEP8 + (P. Papics) fixed a bug when average_brightness was zero
# v0018: (S. Maerivoet) code review and reformatting
# v0017: (P. Papics) make sure that data transfer to the server is in small enough chunks if the data is large
# v0016: (P. Papics) if there is no connection to the server for some reason (wifi/server down), then observations will still continue and data will be saved to a buffer
# v0015: (P. Papics) sending the data to the central server
# v0014: (P. Papics) recording the begin and end of observing intervals, so correction factors can be calculated for downtime. Frame rotation option added. Speed is now correctly new-old and not the other way around...
# v0013: (P. Papics) removed the memory leak introduced in v0012
# v0012: (P. Papics) use MAC address instead of telraam ID, differentiate between no observed objects or too dark to observe
# v0011: (P. Papics) can run continuously and will only observe if the calculated background is bright enough
# v0010: (P. Papics) refined simple tracking algorithm
# v0009: (P. Papics) separated/reorganised tracking/ID loop so later it is easier to do it in post-processing
# v0008: (P. Papics) minor corrections
# v0007: (P. Papics) manual camera controls
# v0006: (P. Papics) switched to time index instead of frame number, and during tracking only those IDs are considered that were actually observed the previous frame
# v0005: (P. Papics) separated detection and tracking loop (tracking is moved to data dump instead of real time)

import warnings
import numpy as np
import cv2
import time
import pandas as pd
import socket
import argparse
import pathlib
import subprocess
import uuid
import json
import requests

__version__ = '2019.03.14'
warnings.simplefilter(action='ignore', category=FutureWarning)

# Parameter definitions

X_RESOLUTION = 1280
Y_RESOLUTION = 720
VIDEO_FPS = 40  # 40 FPS is the top value for larger FOV at 720p, at FPS > 40 the FOV gets narrower!
X_RESIZE_PERCENTAGE = 50  # Horizontal processing resolution in percentage of the recording resolution
Y_RESIZE_PERCENTAGE = 50  # Vertical processing resolution in percentage of the recording resolution
BINARY_THRESHOLD_ABOVE_50PC_OF_HISTOGRAM = 18  # 24 # The threshold in the graysale image for deciding if a deviation from the background is an object or not, relative to the point in the histogram under which 50 percent of total intensity can be found
MIN_OBJECT_PERCENTAGE_OF_IMAGE = 0.1
MAX_OBJECT_PERCENTAGE_OF_IMAGE = 100
AREA_EDGE_X_PERCENTAGE = 25  # Percentage of the image horizontally to be used as buffer area
AREA_EDGE_Y_PERCENTAGE = 0  # Percentage of the image vertically to be used as buffer area
MAX_CONTOURS_BETWEEN_DATA_DUMP = 100000  # This is a hard limit, when reached there will be a data dump, no matter what
PREFERRED_CONTOURS_BETWEEN_DATA_DUMP = 50000  # This is the preferred number, from here on if there is no objects on the screen there will ba a data dump
MAX_TIME_BETWEEN_DATA_DUMP = 60  # 120  # This is a hard limit, if this much time has passed, there will be a data dump no matter what
PREFERRED_TIME_BETWEEN_DATA_DUMP = 30  # 60  # Preferred number of seconds between data dumps, from here on if there is no objects on the screen there will ba a data dump
MIN_FRAMES_FOR_BACKGROUND = 100  # 300
MIN_TIME_FOR_BACKGROUND = 30  # 60
MAX_TIME_BETWEEN_BACKGROUND = 180  # 360
PREFERRED_TIME_BETWEEN_BACKGROUND = 150  # 300

# Database related definitions

URL_RAW_CONTOURS = 'https://telraam-api.net/v0/rawcontours'
HEAD_RAW_CONTOURS = {'Content-Type': "application/json", 'cache-control': "no-cache"}
URL_SUMMARY = 'https://telraam-api.net/v0/summaries'
HEAD_SUMMARY = {'Content-Type': "application/json", 'cache-control': "no-cache"}
URL_UPTIME = 'https://telraam-api.net/v0/uptimes'
HEAD_UPTIME = {'Content-Type': "application/json", 'cache-control': "no-cache"}
MAX_JSON_LENGTH = 5000  # maximum length of data transfer (hard limit at server side is now set at 10000, so never go above that!)

dict_list_raw_contours = []
dict_list_summary = []
dict_list_uptime = []

# Extra parameters calculated using the definitions

X_RESIZED = int(X_RESOLUTION * (X_RESIZE_PERCENTAGE / 100.))
Y_RESIZED = int(Y_RESOLUTION * (X_RESIZE_PERCENTAGE / 100.))
MIN_OBJECT_AREA = ((X_RESIZED * Y_RESIZED) / 100.) * MIN_OBJECT_PERCENTAGE_OF_IMAGE
MAX_OBJECT_AREA = ((X_RESIZED * Y_RESIZED) / 100.) * MAX_OBJECT_PERCENTAGE_OF_IMAGE

print('\n\
 ╔╦╗╦═╗╔═╗╔╗╔╔═╗╔═╗╔═╗╦═╗╔╦╗   ┬   ╔╦╗╔═╗╔╗ ╦╦  ╦╔╦╗╦ ╦\n\
  ║ ╠╦╝╠═╣║║║╚═╗╠═╝║ ║╠╦╝ ║   ┌┼─  ║║║║ ║╠╩╗║║  ║ ║ ╚╦╝\n\
  ╩ ╩╚═╩ ╩╝╚╝╚═╝╩  ╚═╝╩╚═ ╩   └┘   ╩ ╩╚═╝╚═╝╩╩═╝╩ ╩  ╩ \n\
  ┬  ┌─┐┬ ┬┬  ┬┌─┐┌┐┌                                  \n\
  │  ├┤ │ │└┐┌┘├┤ │││                                  \n\
  ┴─┘└─┘└─┘ └┘ └─┘┘└┘                                  ')
print('\n\
 ████████╗███████╗██╗     ██████╗  █████╗  █████╗ ███╗   ███╗\n\
 ╚══██╔══╝██╔════╝██║     ██╔══██╗██╔══██╗██╔══██╗████╗ ████║\n\
    ██║   █████╗  ██║     ██████╔╝███████║███████║██╔████╔██║\n\
    ██║   ██╔══╝  ██║     ██╔══██╗██╔══██║██╔══██║██║╚██╔╝██║\n\
    ██║   ███████╗███████╗██║  ██║██║  ██║██║  ██║██║ ╚═╝ ██║\n\
    ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝')
print('    Version:', __version__)

# Possibility to run with extra output for testing

parser = argparse.ArgumentParser()
parser.add_argument('--test', help='Testing mode on.', action='store_true')
parser.add_argument('--idandtrack', help='Simple object identification and tracking enabled.', action='store_true')
parser.add_argument('--display', help='Display mode on.', action='store_true')
parser.add_argument('--fov', help='Set up the field of view.', action='store_true')
parser.add_argument('--rotate', dest='field_rotation', help='Set rotation angle for the camera (0 or 180, default is 180).', default=180, metavar='0')
args = parser.parse_args()
if args.test:
    print('Running in test mode (minimal slowdown, produces extra data files, background images, on-screen text).')
if args.idandtrack:
    print('Running with a simple object identification and tracking enabled (takes some extra time, produces extra data files with data per IDd object - mergers are not handled).')
if args.display:
    print('Running with continuous image display on (slow, only use for testing).')
if args.fov:
    print('Running only to show the field ov view.')
field_rotation = args.field_rotation

# Initialise manual settings on the camera

exposure_time = 100  # 100 equals to 10 ms (0.01 s = 1/100 s), also this can not be more than 1/FPS so at 60 FPS the max exposure time is ~1/60 = 0.016s -> 160, at 30 FPS it is 320.
cam_props = {'brightness': 50, 'contrast': 15, 'saturation': 0, 'red_balance': 1500, 'blue_balance': 1400, 'sharpness': 0,
             'color_effects': 0, 'rotate': field_rotation, 'video_bitrate_mode': 1, 'video_bitrate': 20000000, 'auto_exposure': 1, 'exposure_time_absolute': exposure_time,
             'white_balance_auto_preset': 0, 'iso_sensitivity_auto': 0, 'iso_sensitivity': 1, 'compression_quality': 100}  # For some reason ISO sensitivity does not seem to work at all
for key in cam_props:  # Here we basically set all camera properties to manual, so they don't change during observing spells between data dumps
    subprocess.call(['v4l2-ctl -d /dev/video0 -c {}={}'.format(key, str(cam_props[key]))], shell=True)

# Functions


def set_exposure_time(number_of_frames):
    global exposure_time, cap, error_msg
    if args.test:
        print('Adjusting exposure time:')
    average_brightness = 0
    exposure_time_old = 0
    # We want to bring the average brightness level to the frame to 127
    while average_brightness < 122 or average_brightness > 132:
        # If the projected exposure time would be longer than what can be achieved at a given framerate, then set the exposure time to the longest possible, and live with it
        if exposure_time/10000. > 1./VIDEO_FPS:
            cap.release()
            initialise_video_capture()
            exposure_time = int((1. / VIDEO_FPS) * 10000)
            subprocess.call(['v4l2-ctl -d /dev/video0 -c {}={}'.format('exposure_time_absolute', str(exposure_time))], shell=True)
            if args.test:
                print('Scene is too dark for optimal exposure time! ( Exposure setting:', exposure_time, ')')
            break
        # If there is no change during the iteration of the exposure time (can happen when the exposure time is very short, and the small change needed to match the actual criteria does not add up to a difference of 1 in the integer exposure time, leading to an infinite loop)
        if exposure_time == exposure_time_old:
            cap.release()
            initialise_video_capture()
            subprocess.call(['v4l2-ctl -d /dev/video0 -c {}={}'.format('exposure_time_absolute', str(exposure_time))], shell=True)
            if args.test:
                print('Scene is likely quite bright, no change in exposure time during the iteration process! ( Exposure setting:', exposure_time, ')')
            break
        averages = np.zeros(int(number_of_frames))
        cap.release()  # We need to always stop and start up the video after all commands with the v4l2 driver, otherwise the update of parameters takes a few frames to materialise
        initialise_video_capture()
        for i in range(int(number_of_frames)):
            ret, frame = cap.read()  # Get frame
            frame_small = cv2.resize(frame, (X_RESIZED, Y_RESIZED), interpolation=cv2.INTER_LINEAR)
            frame_gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
            averages[i] = np.average(frame_gray)
        average_brightness = max(np.average(averages), 0.001)
        exposure_time_old = exposure_time
        exposure_time = max(int(exposure_time * (127 / average_brightness)), 1)  # Estimated exposure time to bring the average brightness to 127 (minimum 1!)
        if args.test:
            print('Frame brightness (at exposure setting) [individual values] calulated exposure setting:', average_brightness, '(', int(exposure_time_old), ')', averages, int(exposure_time))
        subprocess.call(['v4l2-ctl -d /dev/video0 -c {}={}'.format('exposure_time_absolute', str(exposure_time))], shell=True)
    # If it is not bright enough outside, wait 5 minutes and try again (at the end also do a blank data dump just to tell the server we are still up and running)
    if average_brightness < 85:
        if args.test:
            print('It is too dark outside, waiting for more light (empty data dump will happen)...')
        error_msg = -1
    # If it is too bright outside, wait 5 minutes and try again (at the end also do a blank data dump just to tell the server we are still up and running)
    elif average_brightness > 170:
        if args.test:
            print('It is too bright outside, waiting for less light (empty data dump will happen)...')
        error_msg = -2
    else:
        error_msg = 0


def initialise_video_capture():
    global cap
    cap = cv2.VideoCapture(0)
    cap.set(3, X_RESOLUTION)
    cap.set(4, Y_RESOLUTION)
    cap.set(5, VIDEO_FPS)


def background_calculation():
    global background_time, time_data_pocket_end, time_start, error_msg
    error_msg = -9  # Fake value so the loop below can nicely execute
    # Try setting the exposure time until the light conditions are suitable
    while error_msg != 0:
        set_exposure_time(10)
        # If conditions are not suitable, wait five minutes then send out a data dump which will contain the error message
        if error_msg != 0:
            time_start = time.time()
            time.sleep(300)
            data_dump()
    if args.test:
        print('Calculating background...')
    background_time_start = time.time()
    background_time = background_time_start
    background = None
    while background is None or np.shape(background)[2] < MIN_FRAMES_FOR_BACKGROUND or background_time-background_time_start < MIN_TIME_FOR_BACKGROUND:
        ret, frame = cap.read()  # Get frame
        frame_small = cv2.resize(frame, (X_RESIZED, Y_RESIZED), interpolation=cv2.INTER_LINEAR)
        if args.display:
            display = live_view(frame_small)
            if display == 0:
                exit()
        frame_gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
        frame_gray = np.array(frame_gray[:, :, np.newaxis], np.uint8)  # Give array an extra dimension so when we concatenate such arrays there is a third dimension along which it can be done
        if background is None:
            background = frame_gray
        else:
            background = np.concatenate((background, frame_gray), axis=2)
        background_time = time.time()
    medianimage = np.median(background, axis=2)
    if args.test:
        imagefilename = 'test/backgrounds/background_' + str(int(background_time_start)) + '.png'
        cv2.imwrite(imagefilename, medianimage)
    if args.test:
        print('Finished background calculation.')
    time_data_pocket_end = time.time()  # Save the time of the end of the background calculation, since before all background calibrations (except the first) there is a data transfer
    time_start = time_data_pocket_end
    return medianimage.astype('uint8')


def initialise_contour_collector():  # This needs to be called after every data dump so we start collecting contours into an empty array (framenumber only used in FPS calculation)
    global frame_number, number_of_contours, contour_collector
    frame_number = 0
    number_of_contours = 0
    contour_collector = np.zeros((MAX_CONTOURS_BETWEEN_DATA_DUMP, 6))  # This will store all contours' properties from all frames between data dumps


def set_binary_threshold(image):  # Define a binary threshold relative to the histogram of the image (only works on grayscale images!)
    hist_item = cv2.calcHist([image], [0], None, [256], [0, 256])
    binary_threshold = np.argwhere(np.abs(np.cumsum(hist_item)-0.50*np.cumsum(hist_item)[-1]) == np.min(np.abs(np.cumsum(hist_item)-0.50*np.cumsum(hist_item)[-1])))[0][0] + BINARY_THRESHOLD_ABOVE_50PC_OF_HISTOGRAM
    if args.display:
        hist_image = np.zeros((300, 256, 3))  # This will be the image of the histogram
        cv2.normalize(hist_item, hist_item, 0, 255, cv2.NORM_MINMAX)  # Normalise histogram so maximum is 255
        hist = np.int32(np.around(hist_item))
        # Draw histogram line by line
        for x, y in enumerate(hist):
            cv2.line(hist_image, (x, 0), (x, y), (255, 255, 255))
        cv2.line(hist_image, (binary_threshold - BINARY_THRESHOLD_ABOVE_50PC_OF_HISTOGRAM, 0), (binary_threshold - BINARY_THRESHOLD_ABOVE_50PC_OF_HISTOGRAM, 299), (0, 0, 255))  # Annotate the 50% level of total intensity in the histogram
        cv2.line(hist_image, (binary_threshold, 0), (binary_threshold, 299), (255, 0, 0))  # Annotate the binary threshold
        hist_image = np.flipud(hist_image)
        cv2.imshow('bg.-removed hist.', hist_image)
    return binary_threshold


def find_contours(image):  # Defining how contours are found in a background-removed image
    blur = cv2.blur(image, (10, 10))  # Gaussian blur applied to the background-removed image
    binarythreshold = set_binary_threshold(image)  # Get threshold setting
    ret, thresh1 = cv2.threshold(blur, binarythreshold, 255, cv2.THRESH_BINARY)  # Making the-background removed image binary
    im2, contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # Find contours (find the circumference of the objects)
    return contours, hierarchy


def find_objects(contours, hierarchy):  # Defining the object ifentification from a set of contours
    cxs = np.zeros(len(contours))  # Vectors to put the centroid positions of the contours
    cys = np.zeros(len(contours))
    object_areas = np.zeros(len(contours))
    ws = np.zeros(len(contours))
    hs = np.zeros(len(contours))
    for i in range(len(contours)):
        if hierarchy[0, i, 3] == -1:  # We only want parent contours (so not contours within contours - should not happen in a traffic situation, but still, could be that a dark window gets a contour on a vehicle)
            object_area = cv2.contourArea(contours[i])
            if MAX_OBJECT_AREA > object_area > MIN_OBJECT_AREA:  # If object is large enough to be a positive detection
                x, y, w, h = cv2.boundingRect(contours[i])  # Get bounding box
                M = cv2.moments(contours[i])  # Get moments for centroid calculation
                cx = M['m10'] / M['m00']
                cy = M['m01'] / M['m00']
                if np.abs(cx-X_RESIZED/2) < (X_RESIZED/2)*(1-AREA_EDGE_X_PERCENTAGE/100.) and np.abs(cy-Y_RESIZED/2) < (Y_RESIZED/2)*(1-AREA_EDGE_Y_PERCENTAGE/100.):  # If the object is within the inner area of the frame (not in the buffer)
                    cxs[i] = cx  # We add the centroid positions into our lists
                    cys[i] = cy
                    object_areas[i] = object_area
                    ws[i] = w
                    hs[i] = h
    cxs = cxs[cxs != 0]  # Remove centroids that were not inside our main area (but in the buffer)
    cys = cys[cys != 0]
    object_areas = object_areas[object_areas != 0]
    ws = ws[ws != 0]
    hs = hs[hs != 0]
    return cxs, cys, object_areas, ws, hs


def annotate_contours(image, contours, hierarchy, cxs, cys, object_areas, ws, hs):  # Function that adds all contours and their information to an image to be displayed later on
    for i in range(len(contours)):
        if hierarchy[0, i, 3] == -1:  # If contour is a parent
            if MAX_OBJECT_AREA > cv2.contourArea(contours[i]) > MIN_OBJECT_AREA:  # If object is large enough to be a positive detection
                image = cv2.drawContours(image, [contours[i]], 0, (255, 0, 0), 3)
            else:
                image = cv2.drawContours(image, [contours[i]], 0, (255, 0, 0), 1)
        else:
            image = cv2.drawContours(image, [contours[i]], 0, (0, 0, 255), 1)
    for i in range(len(cxs)):  # For the contours that were added to the list as their centroid is inside the main image area and not in the buffer
        cv2.circle(image, (int(cxs[i]), int(cys[i])), 1, (0, 255, 255), 5)  # Plot the centroid
        cv2.putText(image, "A={}".format(str(int(object_areas[i]))), (int(cxs[i]), int(cys[i])), font, 0.5, (0, 255, 0), 2, cv2.LINE_AA)  # Plot data of the object
        cv2.putText(image, "w={}".format(str(int(ws[i]))), (int(cxs[i]), int(cys[i]-20)), font, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(image, "h={}".format(str(int(hs[i]))), (int(cxs[i]), int(cys[i]-40)), font, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(image, "x={}".format(str(int(cxs[i]))), (int(cxs[i]), int(cys[i]-60)), font, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(image, "y={}".format(str(int(cys[i]))), (int(cxs[i]), int(cys[i]-80)), font, 0.5, (0, 255, 0), 2, cv2.LINE_AA)


def id_and_track(contour_collector):
    global total_obs_objects
    contour_collector = contour_collector[0:number_of_contours]  # Drop lines where no contours were filled in
    object_ids = []  # Empty list to keep track of object IDs
    total_obs_objects = 0
    data_frame_time_stamps = np.unique(contour_collector[:, 0])  # List of unique time stamps of all contours (basically the timestamps of all individual frames)
    data_frame = pd.DataFrame(index=data_frame_time_stamps)
    data_frame.index.name = "Timestamp"
    # If there were contours observed (otherwise the for cycle below is skipped anyway and an empty data_frame is returned)
    if len(data_frame_time_stamps):
        old_frame_time = data_frame_time_stamps[0]
        for time_stamp in data_frame_time_stamps:
            frame_time = time_stamp
            cxs = contour_collector[:, 1][contour_collector[:, 0] == time_stamp]
            cys = contour_collector[:, 2][contour_collector[:, 0] == time_stamp]
            object_areas = contour_collector[:, 3][contour_collector[:, 0] == time_stamp]
            ws = contour_collector[:, 4][contour_collector[:, 0] == time_stamp]
            hs = contour_collector[:, 5][contour_collector[:, 0] == time_stamp]
            matched_object_indices = []  # We keep track here of object indexes that have been matched to previously observed objects
            if len(cxs):  # If there are objects in the frame
                if not object_ids:  # If we have no objects tracked at the moment
                    for i in range(len(cxs)):  # For each centroid
                        object_ids.append(total_obs_objects)  # Add ID to the list of object_ids
                        data_frame[total_obs_objects] = ''  # Add column to data frame that will track given vehicle
                        cdx = np.nan  # The delta in position compared to the previous frame will be obviously zero
                        cdy = np.nan
                        data_frame.at[frame_time, total_obs_objects] = np.array([frame_time, cxs[i], cys[i], cdx, cdy, object_areas[i], ws[i], hs[i]])
                        total_obs_objects += 1
                else:  # If we already have tracked objects
                    dxs = np.zeros((len(cxs), len(object_ids)))  # New arrays to calculate position deltas to each tracked object
                    dys = np.zeros((len(cys), len(object_ids)))
                    for i in range(len(cxs)):  # For each centroid
                        for j in range(len(object_ids)):
                            old_cxcy = data_frame.at[old_frame_time, object_ids[j]][1:3]  # Gets centroid coordinates for that objectID from previous frame
                            new_cxcy = np.array([cxs[i], cys[i]])  # The centroids of objects in the current frame
                            if len(old_cxcy) == 0:  # If there is just a new vehicle on this frame, that will not be there on the previous frame, and vehicles that have left the field will also be not there anymore, so then we just go to the next vehicles
                                continue
                            else:  # We calculate the differences between current and old centroids
                                dxs[i, j] = new_cxcy[0] - old_cxcy[0]
                                dys[i, j] = new_cxcy[1] - old_cxcy[1]
                    for j in range(len(object_ids)):
                        sum_cdeltas = np.abs(dxs[:, j]) + np.abs(dys[:, j])  # The sum of coordinate differences for each centroid
                        matched_object_index = np.argmin(np.abs(sum_cdeltas))  # Where the absolute value of the sum is smallest is the matching object (if there is a matching one)
                        min_dx = dxs[matched_object_index, j]  # Value of delta coordinate of centroid for the best match (THIS NEEDS TO BE CHECKED IF LESS THEN MAXIMUM ALLOWED, AND IF SPEED IS SIMILAR TO PREVIOUS IF THAT WAS NOT 0)
                        min_dy = dys[matched_object_index, j]
                        if np.all(dxs[:, j] == 0) and np.all(dys[:, j] == 0):  # If there is no object with that ID in the previous frame, all arrays will be empty
                            continue
                        if frame_time - old_frame_time > 2/fps:  # If the previous frame was too long time ago, we probably are not seeing the same object (ACTUALLY IN THE ORIGINAL SCRIPT WE ONLY LOOKED BACK TO THE PREVIOUS FRAME BUT HERE WE ONLY STORED FRAMES WITH OBSERVATIONS...)
                            continue
                        if matched_object_index in matched_object_indices:  # This is needed so two previously tracked objects don't get matched with the same newly recorded centroid
                            continue
                        else:
                            old_dimension = np.max(data_frame.at[old_frame_time, object_ids[j]][6:8])  # The longer semi axis of the object on the previous frame
                            max_cdelta = old_dimension/2.  # Only allow an object match, if the centroid did not move more than half the objects longer dimension (preferably we would do this separate for x and y dimensions, but if I fit a rotated bounding box, then there is no way to know if height was more in the x or y dimension...)
                            if np.sqrt(min_dx**2 + min_dy**2) < max_cdelta:  # If the centroid with the smallest coordinate difference is within the allowed maximum limit for change in coordinates then we can mathc theat already IDd object with this centroid (so the tracked object can still be seen on this frame)
                                cdx = min_dx  # The coordinate change is then obviosuly the minimum of found coordinate differences
                                cdy = min_dy
                                data_frame.at[frame_time, object_ids[j]] = np.array([frame_time, cxs[matched_object_index], cys[matched_object_index], cdx, cdy, object_areas[matched_object_index], ws[matched_object_index], hs[matched_object_index]])
                                matched_object_indices.append(matched_object_index)  # Keep track that we have already matched this centroid with an existing object
                    for i in range(len(cxs)):  # For all centroids
                        if i not in matched_object_indices:  # That has not been matched with existing objects
                            data_frame[total_obs_objects] = ''  # Create a new column
                            object_ids.append(total_obs_objects)  # Add the new ID to the list
                            cdx = np.nan  # The delta in position compared to the previous frame will be obviously zero
                            cdy = np.nan
                            data_frame.at[frame_time, total_obs_objects] = np.array([frame_time, cxs[i], cys[i], cdx, cdy, object_areas[i], ws[i], hs[i]])
                            total_obs_objects += 1
                    for object_id in object_ids:
                        if data_frame.at[frame_time, object_id] == '':  # Remove object_ids from the list of object_ids that have not been observed in this frame (so in the next cycle they are not matched)
                            object_ids.remove(object_id)
                old_frame_time = frame_time
        if args.test:
            data_filename = 'test/idandtrack/traffic_idandtrack'+str(int(time_data_dump))+'.csv'
            data_frame.to_csv(data_filename, sep=',')
            print('Number of individual object candidates found:', total_obs_objects)
    else:
        if args.test:
            print('Number of individual object candidates found: 0')
    return data_frame


def summary_of_tracked_objects(data_frame):
    object_ids = data_frame.columns
    data_frame.replace('', np.nan, inplace=True)  # Fill the empty cells with NaNs
    data_dump = np.zeros((len(object_ids), 12))  # Create the resulting data array to be filled later (so we don't have to append which is slower)
    d = 0
    for object_id in object_ids:
        dfslice = data_frame[object_id]  # Take the column for that object from the data frame
        dfslice.dropna(inplace=True)  # Cut the NaNs out so only the part of the column remains which contains the IDd object
        dfslicevalues = np.vstack(dfslice.values)  # Transform the data frame (list of numpy arrays at this point) into a 2D numpy array
        if dfslicevalues.shape[0] > 1:  # If something was observed for more than one frame, we calculate averages (otherwise the NaN dx dy would screw up things)
            data_dump[d][1:-3] = np.nanmean(dfslicevalues, axis=0)  # This is the mean of the recorded values over the interval while the object was observed
        else:
            data_dump[d][1:-3] = np.nan_to_num(dfslicevalues)  # For objects that are only on one frame we replace the NaN dx dy values with 0 just to be consistent in the numpy array and have only real numbers
        data_dump[d][0] = hostname
        data_dump[d][1] = np.min(dfslicevalues[:, 0])  # Instead of saving the average time, just save the time of first observation, which is a better property along with the length
        data_dump[d][-3] = np.sqrt((np.max(dfslicevalues[:, 1])-np.min(dfslicevalues[:, 1]))**2 + (np.max(dfslicevalues[:, 2])-np.min(dfslicevalues[:, 2]))**2)  # This is the distance between the two extrema of the observed centroid positions (while average speed might be zero for somebody that walks halfway into the screen then back, this value will still be half the image size)
        data_dump[d][-2] = np.max(dfslicevalues[:, 0])-np.min(dfslicevalues[:, 0])  # This is the total interval of observations for this object (if only one frame this is 0)
        data_dump[d][-1] = dfslicevalues.shape[0]  # This is the number of frames the object was observed for
        d = d+1
    # data_dump = data_dump[data_dump[:, -1]>4]  # Do not report objects that have been visible for less than 5 frmaes (time might be better, but leave it for now)
    # data_dump = data_dump[np.sqrt(data_dump[:, 4]**2 + data_dump[:, 5]**2)>=2]  # Do not report objects where the average speed was less than 2 pixel per frame
    data_dump = data_dump[data_dump[:, -3] > 0.5*(Y_RESIZED*(1-AREA_EDGE_Y_PERCENTAGE))]  # Do not report objects that have a centroid trajectory less than 50% the vertical field of the measuring field (so the vertical image size minus buffer)
    if len(data_dump) == 0:  # if there were no objects recorded in the last interval or we just threw all of them out as negative detections, still put some data just to be able to see that the RPi with the TelraamID is still working
        data_dump = np.array([[hostname, time_data_dump, 0, 0, 0, 0, 0, 0, 0, 0, 0, error_msg]])
        positive_detections = 0
    else:
        positive_detections = len(data_dump)
    send_json_summary(data_dump)
    if args.test:
        data_filename = 'test/summary/traffic_summary_' + str(int(time_start)) + '_' + str(int(time_data_dump)) + '_' + str(error_msg) + '.csv'
        np.savetxt(data_filename, data_dump, delimiter=',', fmt='%16i, %16.3f, %8.2f, %8.2f, %+7.2f, %+7.2f, %8.1f, %6.1f, %6.1f, %8.2f, %8.3f, %6i')
        print('Number of positive (tracked) objects:', positive_detections)


def send_json_raw_contours(data, url=URL_RAW_CONTOURS, head=HEAD_RAW_CONTOURS):
    global dict_list_raw_contours
    keys = ['mac', 'time', 'x', 'y', 'area', 'width', 'height']
    i = 0
    while i < len(data):
        entry = [int(data[i][0]), data[i][1], data[i][2], data[i][3], data[i][4], int(data[i][5]), int(data[i][6])]
        dict_list_raw_contours.append(dict(zip(keys, entry)))
        i = i+1
    try:
        # Make sure that we only clean the dictionary list when the data transfer was successful, otherwise we keep it as a buffer and will transfer more data the next time
        while len(dict_list_raw_contours) > 0:
            if len(dict_list_raw_contours) > MAX_JSON_LENGTH:  # We cut the data into multiple parts if it is too long to be transferred in one go
                dict_list_raw_contours_payload = dict_list_raw_contours[:MAX_JSON_LENGTH]
                dict_list_raw_contours_rest = dict_list_raw_contours[MAX_JSON_LENGTH:]
            else:
                dict_list_raw_contours_payload = dict_list_raw_contours
                dict_list_raw_contours_rest = []
            payload = json.dumps(dict_list_raw_contours_payload)
            ret = requests.post(url, headers=head, data=payload)
            if ret.status_code != 200:  # If the data transfer gave an error, we go and try again
                raise Exception(ret.content)
            dict_list_raw_contours = dict_list_raw_contours_rest  # Only if the data transfer for one segment went through, will we pass to the next segment, or to an empty list at the end
    except Exception as e:
        if args.test:
            print('Transfer of raw contours to the server failed, will retry in the next cycle.')
            print(e)
        pass


def send_json_summary(data, url=URL_SUMMARY, head=HEAD_SUMMARY):
    global dict_list_summary
    keys = ['mac', 'time_start', 'pos_x', 'pos_y', 'spd_x', 'spd_y', 'area', 'width', 'height', 'dist', 'vis_sec', 'vis_fr']
    i = 0
    while i < len(data):
        entry = [int(data[i][0]), data[i][1], data[i][2], data[i][3], data[i][4], data[i][5], data[i][6], data[i][7], data[i][8], data[i][9], data[i][10], int(data[i][11])]
        dict_list_summary.append(dict(zip(keys, entry)))
        i = i+1
    try:
        # Make sure that we only clean the dictionary list when the data transfer was successful, otherwise we keep it as a buffer and will transfer more data the next time
        while len(dict_list_summary) > 0:
            if len(dict_list_summary) > MAX_JSON_LENGTH:  # We cut the data into multiple parts if it is too long to be transferred in one go
                dict_list_summary_payload = dict_list_summary[:MAX_JSON_LENGTH]
                dict_list_summary_rest = dict_list_summary[MAX_JSON_LENGTH:]
            else:
                dict_list_summary_payload = dict_list_summary
                dict_list_summary_rest = []
            payload = json.dumps(dict_list_summary_payload)
            ret = requests.post(url, headers=head, data=payload)
            if ret.status_code != 200:  # If the data transfer gave an error, we go and try again
                raise Exception(ret.content)
            dict_list_summary = dict_list_summary_rest  # Only if the data transfer for one segment went through, will we pass to the next segment, or to an empty list at the end
    except Exception as e:
        if args.test:
            print('Transfer of summary data to the server failed, will retry in the next cycle.')
            print(e)
        pass


def send_json_uptime(data, url=URL_UPTIME, head=HEAD_UPTIME):
    global dict_list_uptime
    keys = ['mac', 'time_start', 'time_end', 'status']
    i = 0
    while i < len(data):
        entry = [int(data[i][0]), int(data[i][1]), int(data[i][2]), int(data[i][3])]
        dict_list_uptime.append(dict(zip(keys, entry)))
        i = i+1
    try:
        # Make sure that we only clean the dictionary list when the data transfer was successful, otherwise we keep it as a buffer and will transfer more data the next time
        while len(dict_list_uptime) > 0:
            if len(dict_list_uptime) > MAX_JSON_LENGTH:  # We cut the data into multiple parts if it is too long to be transferred in one go
                dict_list_uptime_payload = dict_list_uptime[:MAX_JSON_LENGTH]
                dict_list_uptime_rest = dict_list_uptime[MAX_JSON_LENGTH:]
            else:
                dict_list_uptime_payload = dict_list_uptime
                dict_list_uptime_rest = []
            payload = json.dumps(dict_list_uptime_payload)
            ret = requests.post(url, headers=head, data=payload)
            if ret.status_code != 200:  # If the data transfer gave an error, we go and try again
                raise Exception(ret.content)
            dict_list_uptime = dict_list_uptime_rest  # Only if the data transfer for one segment went through, will we pass to the next segment, or to an empty list at the end
    except Exception as e:
        if args.test:
            print('Transfer of uptime data to the server failed, will retry in the next cycle.')
            print(e)
        pass


def data_dump():
    global frame_number, number_of_contours, contour_collector, time_data_pocket_end, time_start, fps, time_data_dump
    time_end = time.time()
    time_data_dump = time_end
    fps = frame_number/(time_end-time_start)
    if args.test:
        print('Data dump in progress...')
        print('FPS since last data dump (/s):', fps)
        print('Total number of contours observed:', number_of_contours)
        data_filename = 'test/rawcontours/traffic_rawcontours_'+str(int(time_start))+'_'+str(int(time_data_dump))+'_'+str(error_msg)+'.csv'
    uptime_data = np.array([[hostname, time_start, time_data_dump, error_msg]])
    send_json_uptime(uptime_data)
    #if number_of_contours > 0:
    #    hostname_column = np.ones(number_of_contours)*hostname
    #    raw_contours_data = np.column_stack((hostname_column, contour_collector[0:number_of_contours]))
    #    send_json_raw_contours(raw_contours_data)
    #    if args.test:
    #        np.savetxt(data_filename, raw_contours_data, delimiter=',', fmt='%16i, %16.3f, %8.2f, %8.2f, %8.1f, %6.1f, %6.1f')
    #else:  # We just send a signal with the hostname and zeros plus a possible error message
    #    raw_contours_data = np.column_stack((hostname, time_data_dump, 0, 0, 0, 0, error_msg))
    #    send_json_raw_contours(raw_contours_data)
    #    if args.test:
    #        np.savetxt(data_filename, raw_contours_data, delimiter=',', fmt='%16i, %16.3f, %8.2f, %8.2f, %8.1f, %6.1f, %6.1f')
    if args.idandtrack:
        data_frame = id_and_track(contour_collector)
        summary_of_tracked_objects(data_frame)
    initialise_contour_collector()
    time_data_pocket_end = time.time()  # Save the time of the last data pocket
    time_start = time_data_pocket_end
    data_dump_duration = time_start-time_end
    if args.test:
        print('Data dump duration (s):', data_dump_duration)


def live_view(image):  # Define simple plotting function for live view testing
    cv2.imshow('frame', image)  # Display the resulting frame
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Stop process when 'q' is pressed
        data_dump()
        cap.release()
        cv2.destroyAllWindows()
        return 0
    else:
        return 1


def field_of_view(image):  # Define simple plotting function for field-of-view setup
    cv2.imshow('frame', image)  # Display the resulting frame
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Stop process when 'q' is pressed
        cap.release()
        cv2.destroyAllWindows()
        return 0
    else:
        return 1

# Here we define some aids

mac_addr = uuid.getnode()  # This gets the MAC address in decimal, mac_addr = hex(uuid.getnode()).replace('0x','') would be the actual MAC address
hostname = mac_addr  # Use the MAC address in the data files as opposed to the  telraam ID
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # Blurring kernel definition
font = cv2.FONT_HERSHEY_SIMPLEX
pathlib.Path('./test').mkdir(parents=True, exist_ok=True)  # Creates test directory should it not exist yet
pathlib.Path('./test/backgrounds').mkdir(parents=True, exist_ok=True)  # Creates test directory should it not exist yet
pathlib.Path('./test/rawcontours').mkdir(parents=True, exist_ok=True)  # Creates test directory should it not exist yet
pathlib.Path('./test/idandtrack').mkdir(parents=True, exist_ok=True)  # Creates test directory should it not exist yet
pathlib.Path('./test/summary').mkdir(parents=True, exist_ok=True)  # Creates test directory should it not exist yet
last_frame_is_empty = 0

# Here we start the camera

initialise_video_capture()
initialise_contour_collector()

# Here a possible loop to set up the field of view

if args.fov:
    while(True):
        setexposuretime(10)
        ret, frame = cap.read()
        frame_small = cv2.resize(frame, (X_RESIZED, Y_RESIZED), interpolation=cv2.INTER_LINEAR)
        frame_small = cv2.rectangle(frame_small, ((int(X_RESIZED*(AREA_EDGE_X_PERCENTAGE/100.)/2.)), (int(Y_RESIZED*(AREA_EDGE_Y_PERCENTAGE/100.)/2.))), ((X_RESIZED-int(X_RESIZED*(AREA_EDGE_X_PERCENTAGE/100.)/2.)), (Y_RESIZED-int(Y_RESIZED*(AREA_EDGE_Y_PERCENTAGE/100.)/2.))), (0, 0, 255), 2)  # Plot the buffer area on screen
        display = field_of_view(frame_small)
        if display == 0:
            exit()

# Here we start the actual image processing and tracking loop

background = background_calculation()
while(True):
    ret, frame = cap.read()
    frame_time = time.time()

    frame_small = cv2.resize(frame, (X_RESIZED, Y_RESIZED), interpolation=cv2.INTER_LINEAR)
    frame_gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)

    frame_background_removed = cv2.absdiff(background, frame_gray)
    contours, hierarchy = find_contours(frame_background_removed)
    cxs, cys, object_areas, ws, hs = find_objects(contours, hierarchy)

    if args.display:
        screen = frame_small  # Here you can set which image you want displayed with info overlays
        screen = cv2.rectangle(screen, ((int(X_RESIZED*(AREA_EDGE_X_PERCENTAGE/100.)/2.)), (int(Y_RESIZED*(AREA_EDGE_Y_PERCENTAGE/100.)/2.))), ((X_RESIZED-int(X_RESIZED*(AREA_EDGE_X_PERCENTAGE/100.)/2.)), (Y_RESIZED-int(Y_RESIZED*(AREA_EDGE_Y_PERCENTAGE/100.)/2.))), (0, 0, 255), 2)  # Plot the buffer area on screen
        annotate_contours(screen, contours, hierarchy, cxs, cys, object_areas, ws, hs)
        display = live_view(screen)
        if display == 0:
            break

    number_of_contours_on_frame = len(cxs)
    if number_of_contours_on_frame:  # Check if there are objects in the frame, add contours to contour_collector
        contour_time = np.ones_like(cxs)*frame_time  # Array like other contour properties but containing the timestamp of the frame
        contours_on_frame = np.stack((contour_time, cxs, cys, object_areas, ws, hs), axis=1)  # Creates one array with all data of the contours found on this frame
        try:  # This try/expect is set up, because in very rare circumstances it could occour, that the contour_collector is almost full, and we are trying to index it beyond its length... Then we just state that it should be taken as full instead and that will directly lead to a data dump
            contour_collector[number_of_contours:number_of_contours+number_of_contours_on_frame] = contours_on_frame  # Adds the data of contours from this frame to the contour_collector
        except:
            number_of_contours == MAX_CONTOURS_BETWEEN_DATA_DUMP
        last_frame_is_empty = 0  # This is a flag we will use later to check if it is safe to export data, so we do not export when there are objects on the frame
    else:
        last_frame_is_empty += 1  # This tells how many frames since last object

    number_of_contours = number_of_contours + number_of_contours_on_frame
    frame_number += 1

    if (number_of_contours == MAX_CONTOURS_BETWEEN_DATA_DUMP) or (number_of_contours >= PREFERRED_CONTOURS_BETWEEN_DATA_DUMP and last_frame_is_empty >= 1) or (frame_time - time_data_pocket_end >= MAX_TIME_BETWEEN_DATA_DUMP) or (frame_time - time_data_pocket_end >= PREFERRED_TIME_BETWEEN_DATA_DUMP and last_frame_is_empty >= 1) or (frame_time-background_time > MAX_TIME_BETWEEN_BACKGROUND) or (frame_time-background_time > PREFERRED_TIME_BETWEEN_BACKGROUND and last_frame_is_empty >= 1):  # If we have enough data or we need to make a new calibration run, dump it and clear the data_frame
        data_dump()

    if (frame_time-background_time > MAX_TIME_BETWEEN_BACKGROUND) or (frame_time-background_time > PREFERRED_TIME_BETWEEN_BACKGROUND and last_frame_is_empty >= 1):  # If we have to, we calculate a new background
        background = background_calculation()

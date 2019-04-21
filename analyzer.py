"""
    Security NGX - The next-generation of outdoor camera-based security
    Copyright (C) 2018/2019 Omar Junaid

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""



from imutils.object_detection import non_max_suppression
import numpy as np
import time
import imutils
import cv2
import queue
import threading
import notifier
import datetime

"""
Redo the entire thing...
It only handles one camera.
We pass in a frame, and set a previous frame,
but we do not know which camera the previous frame belongs to.
But first, check lns 138 and 139.
Comment each out and see which one crashes
on the Pi.


SUGGESTION:
One instance of a class called AnalyzerInstance
for each camera. Make this object-oriented!
"""

elapsed_frames = None
first_frame = None

# TODO test on pi

def scan_for_humans(frame):
    current = datetime.datetime.now()


    """
    Scan the frame for any humans (pedestrians).
    """
    frame = imutils.resize(frame, 
                             width=min(400,
                             frame.shape[1]))
    (rects, weights) = people_hog.detectMultiScale(frame, winStride=(4, 4),
        padding=(8, 8), scale=1.05)

    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
   

    for (xA, yA, xB, yB) in pick:
       if elapsed_frames == 0:
           cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
           elapsed_frames += 1
           name = "Events/%d-%d-%d %d-%d-%d.jpg"\
                       % (current.day, current.month, current.year,\
                       current.hour, current.minute, current.second)
           cv2.imwrite(name, frame)
           notifier.send_notification("Pedestrian detected while armed",
                                 "Detected in X: " + str(xA) + ", Y: " + str(yA)
                                 + " at " + str(current), [name])
           return

def scan_for_motion(frame):
    current = datetime.datetime.now()
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)


    if first_frame is None:
      first_frame = gray

    frameDelta = cv2.absdiff(first_frame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
 
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,\
                             cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
        
    for c in cnts:
       # if the contour is too small or too large, or we
       # are out of bounds, ignore it
        (x, y, w, h) = cv2.boundingRect(c)
        if cv2.contourArea(c) < json_obj["motion_detection"]["min_area_px"]\
        or cv2.contourArea(c) > json_obj["motion_detection"]["max_area_sq_px"]:
            elapsed_frames = max(0, elapsed_frames - 1)
            return
        for zone in json_obj["motion_detection"]["exclusion_zones"]:
           for attr, val in zone.items():
               if (x > val[0] - val[2] and x < val[0] + val[2])\
               or (y > val[1] - val[2] and y < val[1] + val[2]):
                    elapsed_frames = max(0, elapsed_frames - 1)
                    return
        if elapsed_frames == 0:
            elapsed_frames += 1
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            name = "Events/%d-%d-%d %d-%d-%d.jpg"\
                       % (current.day, current.month, current.year,\
                       current.hour, current.minute, current.second)
            cv2.imwrite(name, frame)
            notifier.send_notification("Motion detected while armed",\
                                 "Detected in X: " + str(x) + ", Y: " + str(y)\
                                 + " at " + str(current), [name])
            return

    elapsed_frames = max(0, elapsed_frames - 1)

def analyze_frame(frame, json_obj):
    global first_frame
    if frame is None:
        first_frame = None
        print("Frame analysis error (frame is None). Skipping frame.")
        return
    
    if json_obj["motion_detection"]["masking_division_enabled"]:
        frame = frame[int(frame.shape[0]/json_obj["motion_detection"]["masking_divisor"]\
        ):int(frame.shape[0])]

    global elapsed_frames
    #scan_for_humans(frame) 
    scan_for_motion(frame)
    



def analyze_frames_loop(j):
    while True:
        if not analysis_queue.empty():
            analyze_frame(analysis_queue.get(), json_obj=j)
        time.sleep(1) # Take A LOT burden off the CPU...

def start_analysis_queue_engine(json):
        global elapsed_frames
        if elapsed_frames is None:
            elapsed_frames = 0
        global count
        count = 0
        global people_hog
        people_hog = cv2.HOGDescriptor()
        people_hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        global analysis_queue
        analysis_queue = queue.Queue()
        analysis_thread = threading.Thread(target=analyze_frames_loop, 
                                           args=(json,))
        analysis_thread.daemon = True
        analysis_thread.start()
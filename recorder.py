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
import captureservice as cs
import cv2
import datetime
import pathlib
import analyzer
import os
import time 
import sys
import main
import numpy as np


from sys import platform
from main import *


"""
Create the files we need for recording.

@param vc_obj The OpenCV VideoCapture object
we want to record from.

@param cam_obj The Camera object (camera.py)
we want to record from (this has the attributes
we need such as name, feed, audio etc)
"""

def create_recording_files(vc_obj, cam_obj):
        p = main.data["loop_recording"]["delete_after_days"]
        now = datetime.datetime.now()
        base_dir_name = str(now.year) + '-' + str(now.month)

       
        frame_width, frame_height = vc_obj.get_size()
        
        pathlib.Path(
            'Recordings/'
            ).mkdir(parents=False, exist_ok=True) 

        pathlib.Path(
            'Recordings/' + cam_obj.name
            ).mkdir(parents=True, exist_ok=True) 

        pathlib.Path(
            'Recordings/' + cam_obj.name + "/" + base_dir_name
            ).mkdir(parents=True, exist_ok=True) 

        pathlib.Path(
            'Recordings/' + cam_obj.name + "/" + base_dir_name + "/" +
           "Day " + str(now.day)
            ).mkdir(parents=True, exist_ok=True) 

        pathlib.Path(
            'Recordings/' + cam_obj.name + "/" + base_dir_name + "/" +
            "Day " + str(now.day) + "/" + "Hour " + str(now.hour)
            ).mkdir(parents=True, exist_ok=True) 

        entire_path =  "Recordings/" + cam_obj.name + "/" + base_dir_name + "/"\
        + "Day " + str(now.day) + "/"\
        + "Hour " + str(now.hour) + "/"
        
        cam_obj.previous_path = entire_path + str(now.minute) + ".avi"

        cam_obj.writer = cv2.VideoWriter(entire_path + str(now.minute) + ".avi", 
                                 cv2.VideoWriter_fourcc(*'XVID'),
                                 2, 
                                 (int(frame_width), int(frame_height)))



"""
Delete any files older than n days in a specified directory.

@param n Delete any files older than n days
@param directory The directory to delete from
@raises TypeError if invalid or no n argument
"""
def delete_older_than_n_days(n=None, directory="Recordings/"):

    if n is None or not isinstance(n, (int)):
        raise TypeError("Invalid arg (n) to delete_older_than_n_days()")

    now = time.time()
    only_files = []

    for file in os.listdir(directory):
         if os.path.isfile(directory) and file.endswith(file_ends_with):
              #Delete files older than n days
                if os.stat(directory).st_mtime < now - n * 86400:
                      os.remove(directory)


"""
Record from our VideoCapture object
and add every other frame to the 
analysis queue.


@param cam_obj The Camera object (camera.py)
we want to record from (this has the attributes
we need such as name, feed, audio etc)
"""

def record_forever(cam_obj):
    last_frame_second = datetime.datetime.now().second
    if cam_obj.cam_type == 0:
        cap = cs.CaptureService(cam_obj, cs.VideoStreamSource.OPENCV)
    else:
        cap = cs.CaptureService(cam_obj, cs.VideoStreamSource.JPEGSTREAM)

    create_recording_files(cap, cam_obj)
    original_time = datetime.datetime.now()

    print("Started recording camera: "\
          + cam_obj.name)
    
    if (not cap.is_open()): 
        print("Error opening video stream or file: "\
              + cam_obj.name)
 
    # Read until video is completed
    while(True):
         # Capture frame-by-frame
            
            frame = cap.get_frame()
              
            now = datetime.datetime.now()
            cam_obj.frame = frame
            cam_obj.writer.write(frame)
            if main.is_armed and now.second != last_frame_second:
                last_frame_second = now.second
                analyzer.analysis_queue.put(frame, main.data)
          #      cv2.waitKey(20)
            """Every 10 minutes,
            create a new recording file."""
            time_diff = (now\
                         - original_time)\
                         / datetime.timedelta(minutes=1)

            if(time_diff >= float(10)):
                original_time = datetime.datetime.now()
               # if json_obj["ffmpeg"]["compress_and_convert"]:
                  #  ffmpeg_wrapper.compress_and_convert(
                       #                 cam_obj.previous_path)
                create_recording_files(cap, cam_obj)
                delete_older_than_n_days(
                                    main.data["loop_recording"]["delete_after_days"])

    
    cam_obj.writer.release()

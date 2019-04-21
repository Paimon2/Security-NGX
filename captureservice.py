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


import main
from enum import IntEnum
import cv2
import requests
import numpy as np

#todo cleanup imports


class VideoStreamSource(IntEnum):
    OPENCV = 0
    JPEGSTREAM = 1


"""
CaptureService class.
@brief High-level wrappers for various types of streams.
See the CaptureType enumeration for stream types.

@note use repr(enum_item) to convert from enum item to number
"""
class CaptureService(object):

    def __init__(self, cam_obj, source:VideoStreamSource):
        self.cam_obj = cam_obj
        self.in_error_state = False
        if cam_obj.cam_type == VideoStreamSource.OPENCV:
            # create cv2 videocapture object
            self.cap = cv2.VideoCapture(self.cam_obj.feed)
        else: # JPEGSTREAM
            pass #todo
    def __del__(self):
        pass

    def is_open(self):
        if self.cam_obj.cam_type is VideoStreamSource.OPENCV:
            return self.cap.isOpened()
        else:
            return True #todo actually check
    def get_size(self):
        if self.cam_obj.cam_type is VideoStreamSource.OPENCV:
            return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH),\
                    self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT);
        else:
            frame = self.get_frame()
            height, width = frame.shape[:2]
            return width, height

    def get_frame_internal_opencv(self):
        ret, frame = self.cap.read()
        # If the frame appears to be garbage data, assume we
        # are getting bogus data from the source (if any at all).
        # Then, go into an error state and re-establish the connection.
        if not ret or frame is None or frame.size == 0:
            self.in_error_state = True
            return None
        return frame

    """
    Actually get the video frame.
    @case1: Source is OpenCV:
    Get the frame. If the return code
    isn't good, attempt to re-establish the connection.
    @case2: Source is JPEG:
    Fetch the frame via urllib, authenticating if need be.
    """
    def get_frame(self):
        if self.cam_obj.cam_type == VideoStreamSource.OPENCV:
            frame = self.get_frame_internal_opencv()
            if not self.in_error_state:
                return frame
            if self.in_error_state:
                # We're in an error state; the frame isn't valid.
                # Release the capture object and re-establish a connection.
                self.cap.release()
                while frame is None:
                    # Keep trying to re-establish a connection
                    # until we get a non-None frame
                    self.cap = cv2.VideoCapture(self.cam_obj.feed)
                    _, frame = self.cap.read()
                # We've re-established the connection.
                frame = self.get_frame_internal_opencv()
                self.in_error_state = False
                return frame
        if self.cam_obj.cam_type == VideoStreamSource.JPEGSTREAM:
            # Do we need to authenticate?
            p = self.cam_obj.cam_type
            if len(self.cam_obj.additional_data.get("auth_uname")) > 0:
                r = requests.get(self.cam_obj.feed, auth=(
                                                    self.cam_obj.additional_data["auth_uname"], 
                                                    self.cam_obj.additional_data["auth_pass"]))
            else:
                r = None
                try:
                    r = requests.get(self.cam_obj.feed)
                except:
                    pass #todo urgent append to error list then return

            arr = np.asarray(bytearray(r.content), dtype="uint8")
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            return img
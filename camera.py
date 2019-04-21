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

import json

import database
from database import *
import threading
import recorder
from recorder import *


"""
The Camera Class.
TODO documentation
"""
class Camera(object):
     def __init__(self, cam_name):
        self.name = cam_name 
        self.frame = None
        self.previous_path = None
        database.cur.execute ("SELECT * FROM Cameras WHERE name = '"
                             + cam_name + "';")
        for row in database.cur: #todo refactor
            self.feed = row["location"]
            self.cam_type = row["type"]
            self.has_audio = bool(row["has_audio"])
            try:
                self.additional_data = json.loads(row["additional_data"])
            except TypeError:
                self.additional_data = None
     def __del__(self):
        pass

     def get_frame_as_bytes(self):
        _, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg.tobytes()



"""
The DatabaseCamera Class.
TODO documentation
"""
class DatabaseCamera(object):
    def __init__(self, 
                 cam_name, 
                 cam_feed,
                 cam_type, 
                 cam_has_audio,
                 cam_auth_uname = None,
                 cam_auth_pass = None):

        self.name = cam_name
        self.feed = cam_feed
        self.cam_type = cam_type
        self.has_audio = cam_has_audio
        if cam_auth_uname is None:
            cam_auth_uname = ""
        if cam_auth_pass is None:
            cam_auth_pass = ""
        self.additional_data = json.dumps({'auth_uname': cam_auth_uname,\
                                'auth_pass': cam_auth_pass})
    def __del__(self):
        pass

    def add_to_db(self):
         database.cur.execute("INSERT INTO Cameras (name, location, type,"
                             "has_audio, additional_data)"
                       " VALUES ('" + self.name + "',"
                       "'" + self.feed + "',"
                       "'" + str(int(self.cam_type)) + "',"
                       "" + str(int(self.has_audio)) + ","
                       "'" + self.additional_data + "')"
                       )


def start_recording_cameras():
    global cam_list
    cam_list = []
    database.cur.execute("SELECT * FROM Cameras;")
    for row in database.cur:
        current_camera = Camera(row['name'])
        cam_list.append(current_camera)
        recorder_thread = threading.Thread(target=recorder.record_forever,
                                          args=(current_camera,))
        recorder_thread.daemon = True
        recorder_thread.start()


def gen(cam_no):
    while True:
        try:
            frame = cam_list[cam_no].get_frame_as_bytes()
            yield (b'--frame\r\n'\
                   b'Content-Type: image/jpeg\r\n\r\n' + \
                   frame + b'\r\n\r\n')
            time.sleep(0.1)
        except NameError as e:
            print(e) #todo log exception


def get_frame(cam_no):
    return cam_list[cam_no].frame
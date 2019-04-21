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

import cv2

from main import app
from main import access_code
from main import is_armed
from main import files_index
from main import data
import os
import user
import database
import camera
import psutil
from camera import *

from flask import Flask, send_from_directory
from flask import render_template
from flask import Response, session 
from flask import flash, redirect
from flask import render_template, request


from flask_autoindex import AutoIndex


"""
The Flask AutoIndex path.
The end user should be able to request files.
This can be essential when the user's browser
is not capable of playing HTML5 audio/video,
and instead the video file must be requested
from the server as a download.
"""

@app.route('/file_browser/')
@app.route('/file_browser/<path:path>')
def autoindex(path='.'):
    if not session.get('logged_in'):
            sess_msg = "Please sign-in to access system files."
            return render_template('/login.html', msg=sess_msg)
    else:
        return files_index.render_autoindex(path)


"""
The root page.
If the user is already logged in, redirect them to the
main index page. If not, send them to the login page.
"""
@app.route('/')
def home():
    """
    If we have a battery, show the battery percentage
    and whether or not the AC adapter is plugged in.
    If we don't, psutil very conveniently makes battery
    a NoneType, so we can just tell the user we don't
    have a battery that way.
    """
    battery = psutil.sensors_battery()
    if battery is None:
        batt_plugged = "No battery detected!"
        batt_percent = 100
    else:
        batt_plugged = battery.power_plugged
        batt_percent = str(battery.percent)

    """
    Something that can be critically important for servers,
    and especially home servers - temperatures. This returns a
    globberjabbering kind of data (seems like variable JSON),
    one that I'm not even going to attempt to parse. Fortunately,
    though, humans CAN read it if they put their
    mind to it (it seriously isn't that hard).

    The (other?) biggest limitation of this is that it's only
    compatible with *nix operating systems. Sorry,
    Windows users.
    """


    if platform == "win32":
            temps = "Feature not supported on Windows"
    else:
            temps = psutil.sensors_temperatures()
    

    if not session.get('logged_in'):
            return render_template('/login.html')
    else:
         pid = os.getpid()
         py = psutil.Process(pid)
         memoryUse = py.memory_info()[0]/2.**30
         return render_template('/index.html',
                               arm_status=main.is_armed,
                               batt_p=batt_percent, 
                               batt_pl=batt_plugged, 
                               cpu_pl=str(psutil.cpu_percent()), 
                               used_ram=str(round(psutil.virtual_memory().used >> 20, 4)),
                               free_disk=str(psutil.disk_usage("/").percent), 
                               temp_current=str(temps),
                               script_ram=str(round(memoryUse * 1000, 4)))


"""
The page where users can view the feed of their cameras.
We pass in the local camera list. Note that this isn't
a DatabaseCamera object, but instead a Camera object.

The difference is that the DatabaseCamera object only contains
a limited amount of camera information - just enough so we can store
its information in the database. The Camera object contains proper information
we'll need to use while recording and analyzing frames
such as last frame, etc. 

So, we'll use all this information to get each camera frame in raw bytes
(JPEG) and continually refresh the feed so as to provide a form of live
streaming. 

Don't worry about managing the list here - that sort of stuff
is handled inside the actual camera.html file.
"""
@app.route('/cameras')
def cameras():
    return render_template('/cameras.html', 
                           camera_list=camera.cam_list)

"""
The settings page which can modify cameras.

We pass in a list of the currently recording cameras
to the template, which then loops over that list
and displays them. This provides the users with an
option of deleting that camera or adding more cameras.
"""
@app.route('/settings_cameras')
def settings_cameras():
    database.cur.execute("SELECT * FROM Cameras;")
    if session.get('logged_in'):
        return render_template('/settings_cameras.html', cur=database.cur)
    else:
        return "You have been logged out, re-login."

"""
The Settings page. Self explanatory.

We pass in a list of the currently recording cameras
to the template, which then loops over that list
and displays them. This provides the users with an
option of deleting that camera or adding more cameras.
"""
@app.route('/settings')
def settings():
   database.cur.execute("SELECT * FROM Cameras;")
   if session.get('logged_in'):
        return render_template('/settings.html', cur=database.cur)
   else:
        return "You have been logged out, re-login."

@app.route('/togglearm')
def togglearm():
    if session.get('logged_in'):
        main.is_armed = not main.is_armed
        return home()

"""
This is a direct link which will be used
for accessing the nth camera feed.

We ask for the camera number (n) in the URI,
then return a Response object which contains
the raw bytes of the camera image (JPEG).
That image is being constantly refreshed to
create an illusion that it is being streamed
(well, in theory, it sort of is!).
The n will be passed onto the list, where it
will try to find the nth camera and return its
Response.
"""
@app.route('/video_feed/<int:cam_no>')
def video_feed(cam_no):
    if not session.get('logged_in'):
        return "Login to view feed"
    return Response(camera.gen(cam_no),\
                    mimetype='multipart/x-mixed-replace; boundary=frame;')

"""
Download a single frame (snapshot) from the camera directly
to the user's computer.
"""
@app.route('/get_snapshot/<int:cam_no>')
def get_snapshot(cam_no):
    if not session.get('logged_in'):
        return "Login to view feed"
    # For now, save it locally then send it.
    # TODO Fix this in the future.
    result = cv2.imwrite("snapshot.jpg", camera.get_frame(cam_no))
    dir = app.root_path
    return send_from_directory(directory=dir, filename="snapshot.jpg")



"""
This subroutine executes a SQL query
to find the camera with the name we specify,
and remove it from the database.

Changes such as stopping recordings will only
take effect after restarting the script.

@param name The name of the camera we
want to delete
"""
@app.route('/del_camera/<name>')
def delete_camera(name):
    if session.get('logged_in'):
         database.cur.execute("DELETE FROM Cameras WHERE name = '"
                             + name + "';")
         flash('Camera deleted successfully.')
         return home()

"""
The template (.html file) to add a camera
"""
@app.route('/settings_cameras_add')
def settings_cameras_add():
    if session.get('logged_in'):
        return render_template('/settings_cameras_add.html')

"""
Here we sign out of the system, by negating a local
session variable and rendering the login page afterwards.
"""
@app.route('/signout')
def signout():
    session['logged_in'] = False
    return render_template('/login.html', msg="Logged out successfully.")

"""
Here users can sign up for the system, provided they
have the access code which is in the application console.
In case the user somehow (it does happen) gets to the register 
page while being logged in, we'll take them back to the login page.
"""
@app.route('/register')
def register():
    if session.get('logged_in'):
        return render_template('/index.html')
    return render_template('/register.html')


"""
Actually login to the database.
This is the actual URI to which we send a POST
request with some login details. We then hash the
password using passlib and execute a SQL query to compare
the two sets of credentials. This process is handled by
database.authenticate(). 
If we verify the login has been successful and the sets of credentials
match, we set the local logged_in session variable to True.
"""
@app.route('/login', methods=['POST'])
def do_login():
   # Reconnect if we timed out
   database.connect(main.data)
   if database.authenticate(request.form['username'],
                          request.form['password']):
       session['logged_in'] = True
       return home()
   return render_template('/login.html', msg="Incorrect username or password.")


"""
This is the URI to which we send a POST request
to add a camera to the database. We need three
*POST method* parameters:

@flask_POST_param cam_name (name of the camera)
@flask_POST_param cam_feed (link to RTSP feed)
@flask_POST_param cam_has_audio (does camera have RTSP audio? (bool))


Changes such as recording cameras will only take effect
after restarting the application, as the local camera list
is not in sync with the SQL database, mainly due to performance
and efficiency reasons.
"""
@app.route('/cam_add_method', methods=['POST'])
def cam_add_method():
    if session.get('logged_in'):
       temp_cam = camera.DatabaseCamera(request.form['cam_name'],
                                request.form['cam_feed'],
                                request.form.get('cam_type_is_mjpeg') is not None,
                                request.form.get('cam_has_audio') is not None,
                                request.form.get('auth_uname'),
                                request.form.get('auth_pass'))
       temp_cam.add_to_db()
       return settings_cameras()
  

"""
The registration page.
The user should be able to register for a new account, but
only if they have the access code which is obtained from the console
to prevent any non-authorized people from accessing this page.
"""
@app.route('/registerform', methods=['POST'])
def do_register():
    if request.form['password'] != request.form['passwordconfirm']:
        return render_template('/register.html', msg="Passwords do not match.")
    if database.user_exists(request.form['username']):
        return render_template('/register.html', msg="A user already exists with that username.")
    if request.form['accesscode'] != str(access_code):
        return render_template('/register.html', msg="Incorrect access code. "
                                "Find it in the application console.")

    current_user = user.User(request.form['username'],
                   request.form['password'],
                   0, 0)

    current_user.add_to_db()
    return render_template('/login.html', msg="Registration successful. You may now log in.")
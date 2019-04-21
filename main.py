#!/usr/bin/python3
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

# First and foremost ALWAYS - the logger
import logging


logging.basicConfig(filename='SecurityNGX.log', 
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger("SecurityNGX.log")
logger.setLevel(logging.INFO)

import random
access_code = random.randint(1000000, 9999999)

import exceptions
import database
import camera
import ffmpeg_wrapper
import ddns
import analyzer
import notifier

from flask import Flask
from flask_autoindex import AutoIndex 

import datetime
import os
import json
import time
import threading
import psutil
import sys
import alerter
import status

"""
Declare our global variables for our Flask application.

"""
is_armed = False
stat_controller = status.StatusController()
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
files_index = AutoIndex(
    app,
    browse_root=os.path.curdir,
    add_url_rules=False)



def load_json():
   logger.info("Loading JSON data from data.json...")
   exists = os.path.isfile('data.json')
   if not exists:
       logger.critical("FATAL ERROR: data.json not found!")
       sys.exit()
   with open('data.json', encoding='utf-8') as f:
        global data
        data = json.load(f)
        # Import the pages (templates) we want to use. TODO put elsewhere
        import pages
        if data is None:
            logger.critical("FATAL ERROR: No configuration file!")
            sys.exit()

def init():
    global is_armed
    is_armed = False
    print("Registration access code is: " 
         + str(access_code))
    load_json()
    app.secret_key = data["flask"]["secret_key"]
    database.connect(data)
    analyzer.start_analysis_queue_engine(data)
    camera.start_recording_cameras()
    notifier.init_notifier(data)
    if data["ddns"]["enabled"]:
        ddns_thread = threading.Thread(target=ddns.update_ddns_forever,\
                                          args=(data,))
        ddns_thread.daemon = True
        ddns_thread.start()

    
    app.run(host="0.0.0.0",
            debug=True,
            use_reloader=True,
            port=data["flask"]["port"],
            passthrough_errors=True,
            threaded=True)




init()

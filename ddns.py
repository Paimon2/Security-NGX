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


"""
    ddns.py
    This file contains methods to send an IP change request
    every X seconds to the free Dynu DDNS Service.

    This is useful for home servers or other environments where
    the IP address may change.

"""

import requests
import time
from time import sleep
import json


# Actually send the request with the params from data.json
def send_ddns_change_request(j):
    DDNS_SERVER_URL = "http://api.dynu.com/nic/update?&username="\
    + j["ddns"]["username"]\
    + "&password="\
    + j["ddns"]["password"]
    req_data = requests.get(DDNS_SERVER_URL)
    content = req_data.content.decode('utf-8')
    if "good" not in content and\
    "nochg" not in content:
        print("DDNS error: " + str(req_data.content))

# Obviously, this will be called from another thread
def update_ddns_forever(j):
    while True:
        send_ddns_change_request(j)
        time.sleep(j["ddns"]["ping_interval"])

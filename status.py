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

from enum import Enum
import urllib
import threading
import time

"""
https://stackoverflow.com/questions/3764291/checking-network-connection
"""
def internet_on():
    try:
        urllib.request.urlopen('http://216.58.192.142', timeout=1)
        return True
    except urllib.error.URLError as err: 
        return False

"""
TODO Scrap this heartbeat system


The heartbeat system.

To ensure all systems are working as intended,
they must send a heartbeat to us at least one time
per minute. 

We wait 20 seconds each minute, then see which services
have not sent a heartbeat to us. We wait another 10 seconds if
they still haven't sent it, then we know there's an issue, and
add it to our issue list.

"""

class HeartbeatSource(Enum):
    RECORDER = 0
    ANALYZER = 1
    CAMERA   = 2


class StatusController(object):
    def __init__(self):

        """
        issues_list is a list which should contain sub-lists.
        We do not opt for tuples here as they are immutable.

        Each sub-list should contain 3 items:

        @item datetime_obj The datetime.datetime object of when
        this issue happened.
        @item issue_str A human-readable string of what happened.
        @item has_expired Has the issue been solved yet?
        """
        self.issues_list = []

    def get_total_issues(self):
        pass


    """
    @param datetime_obj The datetime.datetime object of when
    this issue happened.
    @param issue_str A human-readable string of what happened.
    @param has_expired Has the issue been solved yet?
    """
    def add_issue(datetime_obj, issue_str, has_expired=False):
        issues_list.append([datetime_obj, issue_str, has_expired])

    def get_issues_list(self):
        return self.issues_list
    
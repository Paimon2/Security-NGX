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

import pymysql
import exceptions
import base64
from passlib.apps import custom_app_context as pwd_ctx
from main import logger


# Helper functions
def table_exists(table_name):
    try:
        cur.execute("SELECT 1 FROM " + table_name + " LIMIT 1;")
    except pymysql.err.ProgrammingError: 
        return False
    return True

def user_exists(username):
    if not table_exists("Users"): # just in case
        raise UnderlyingTableNotFoundError()
    cur.execute("SELECT * FROM Users WHERE username = '" + username + "'")
    return cur.fetchone() != None

def authenticate(username, password):
    cur.execute("SELECT password FROM Users WHERE username = %s", (username,))
    try:
         are_pwds_equal = pwd_ctx.verify(password, cur.fetchone()['password'])
         if are_pwds_equal:
             # TODO log login and login time
             return True
         return False
    except:
         return False

"""
Verify the required tables exist in our MySQL database,
and if not, create them.
connect(j) MUST be called before this, as it initalizes
and globalizes the database cursor variable.
""" 
def verify_tables_exist():
    # First off, the Users table
    if not table_exists("Users"):
        logger.info("Users table does not exist, creating it now.")
        cur.execute('CREATE TABLE Users (username varchar(64),'
                    'password varchar(512), last_login_epoch bigint,'
                    'is_admin tinyint, unread_notifications tinyint,'
                    'permissions_json mediumtext);')
    # The Notifications table
    if not table_exists("Notifications"):
        logger.info("Notifications table does not exist, creating it now.")
        cur.execute('CREATE TABLE Notifications (id int, description varchar(64),' 
                    'filename varchar(512), time_epoch int);')
    # The Faces table
    if not table_exists("Faces"):
        logger.info("Faces table does not exist, creating it now.")
        cur.execute('CREATE TABLE Faces (id int, name varchar(64),' 
                    'filename varchar(512));')
    # The Cameras table
    if not table_exists("Cameras"):
        logger.info("Cameras table does not exist, creating it now.")
        cur.execute('CREATE TABLE Cameras (name varchar(64),' 
                    'location varchar(1024), has_audio tinyint,'
                    'type tinyint, additional_data mediumtext);')

"""
Connect to a MySQL database.
The parameter, j, should be a JSON object
that is passed in from main.py. The underlying
data should be pulled from data.json. We then attempt
to establish a connection to a MySQL database, and verify
everything is as we need it to be. If not, we must make corrections,
which includes creating nonexistent tables if required.
"""

def connect(j):
    logger.info("Attempting to connect to the database...")
    try:

        global application_db
        application_db = pymysql.connect(host=j["database"]["host"], 
                                            port=j["database"]["port"], 
                                            user=j["database"]["user"],
                                            passwd=j["database"]["password"],
                                            db=j["database"]["name"],
                                            autocommit=True,
                                            cursorclass=pymysql.cursors.DictCursor)

    except pymysql.err.OperationalError as e:
      logger.critical('FATAL ERROR: Unable to connect to the database.\n'
                      'Here is what pymysql returned: \n'
                      + str(e) + '\n\n\n')
      return

    logger.info("Database connection successful.")
    global cur
    cur = application_db.cursor()
    verify_tables_exist()


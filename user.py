import database
from database import *
from passlib.apps import custom_app_context as pwd_ctx

"""
The User class.

We have the following attributes:
    username : username : string/plaintext
    hashed_password : hashed password : string/hashed
    is_admin : is user administrator? : boolean
    last_login : last login (epoch time) : int
    unread_notifications : amt of unread notifications : int

"""

class User(object):

    def __init__(self, username, password, is_admin, last_login_epoch):
        self.name = username
        self.hashed_password = pwd_ctx.hash(password)
        self.is_admin = is_admin
        self.unread_notifications = 0
        self.last_login_epoch = 0

    def __del__(self):
        pass


    """
    Add the user to the database.
    This assumes an existing record does NOT exist
    in the table.
    """

    def add_to_db(self):
        database.cur.execute("INSERT INTO Users (username, password, last_login_epoch,"
                       " is_admin, unread_notifications)"
                       " VALUES ('" + self.name + "',"
                       "'" + self.hashed_password + "',"
                       "'" + str(self.last_login_epoch) + "',"
                       "'" + str(int(self.is_admin == 'true')) + "',"
                       "'" + str(self.unread_notifications) + "')")

    """
    Write all user information to a MySQL database.
    IMPORTANT: This assumes the user has already been created
    through add_to_db().
    """
    def write_to_db(self):
        database.cur.execute("UPDATE Users"
                       " username = '" + self.name + "',"
                       " password = '" + self.hashed_password + "',"
                       " last_login_epoch = '" + self.last_login_epoch + "',"
                       " is_admin = '" + str(int(self.is_admin == 'true')) + "',"
                       " unread_notifications = '" + str(self.unread_notifications) + "'"
                       " WHERE username = '" + self.username + "';")


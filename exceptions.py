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

from main import logger

# Quick function to log and print an error
def log_exception(msg):
    logger.error(msg)
    print(msg)

"""
The exceptions below define instances at runtime where a required binary
which is to be executed, as part of a subprocess or individually, is not 
present on the system. This includes not being named correctly, not being
in the correct directory or not being a correct binary for the runtime 
operating system. 

The base exception is BinaryNotFoundError, with other exceptions inheriting from this
as well as printing and logging the error.
"""

class BinaryNotFoundError(Exception):
    logger.error('A binary is missing or not named correctly.\n'
                  'Refer to the traceback or line below for more information.\n')


class FFMPEGNotFoundError(BinaryNotFoundError):
   log_exception('A FFMPEG binary was not found or installed in the correct path.\n'
         'Ensure it is named ffmpeg.exe on Windows, ffmpeg.dmg on Mac, and\n'
         'ffmpeg on Linux. It must be placed in the Security NGX scripts directory.\n'
         )

"""
The exceptions below define general media errors. The most commonly used one
would be OpenCVBadCodeError, in case of an unreliable camera setup.

The base exception is MediaActionError, with other exceptions inheriting from this
as well as printing and logging the error.
"""
class MediaActionError(Exception):
    logger.error('An action was unable to be performed on a media medium.\n'
                  'Refer to the traceback or line below for more information.\n')

class OpenCVBadCodeError(MediaActionError):
   log_exception('A connection to a camera was unable to be established.\n'
                 'Attempts will be made to reconnect.\n')
         

"""
The exceptions below define instances at runtime where modifying recorded files may
fail. This includes deleting, renaming, and creating video files.

The base exception is VideoFileModificationError, with other exceptions inheriting from this
as well as printing and logging the error.
"""

class VideoFileModificationError(Exception):
    logger.error('A video file is unable to modified.\n'
                  'Refer to the traceback or line below for more information.\n')

class LoopRecordingDeleteError(VideoFileModificationError):
   log_exception('An old video file was unable to be deleted.\n'
         'Ensure you have given the script adequate permissions.\n'
         )

class LoopRecordingMoveError(VideoFileModificationError):
   log_exception('An old video file was unable to be moved.\n'
         'Ensure you have given the script adequate permissions.\n'
         )

class LoopRecordingRenameError(VideoFileModificationError):
   log_exception('An old video file was unable to be renamed.\n'
         'Ensure you have given the script adequate permissions.\n'
         )

class VideoFileAlreadyExists(VideoFileModificationError):
   log_exception('A video file with the same name exists.\n'
         'A recovered copy will be made, however it is recommended\n'
         'to delete or move files with the same name\n.'
         )


"""
The exceptions below define instances at runtime where a database error may occur.
This includes tables/entries not being found, transit issues and other errors.

The base exception is DatabaseError, with other exceptions inheriting from this
as well as printing and logging the error.
"""

class DatabaseError(Exception):
    logger.error('A database error has occurred.\n'
                  'Refer to the traceback or line below for more information.\n')


class UnderlyingTableNotFoundError(DatabaseError):
     log_exception('A database entry was unable to be modified.\n'
         'Ensure all necessary tables exist.\n'
         )
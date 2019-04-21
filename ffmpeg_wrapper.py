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

import subprocess
import threading
import os
import re


"""
Compress a file with CRF 19 and output it
as MP4. This is an _internal function, so it
must be called from a thread other than the main
one.

@param full_path The FULL path to the file
we want to convert. This includes the extension.
The file name MUST match the regex below.
"""
def compress_and_convert_internal(full_path):
    arguments = ['ffmpeg', '-i', full_path, '-vcodec', 'libx264',
                 '-crf', '19',\
                # A regex expression to replace the .avi file 
                # name with the .mp4 file name (note: raw string literal)
                str(re.sub('([0-9][0-9]).avi', r'\1.mp4', full_path)),\
                ]

    subprocess.call(arguments)
    os.remove(full_path) # Delete the old file once we've processed this one


def add_audio_internal(audio_path, video_path):
    pass #todo implement

def record_audio_internal(audio_path, video_path):
    pass #todo implement



def compress_and_convert(full_path):
    fn_thread = threading.Thread(target=compress_and_convert_internal,
                                 args=(full_path,))
    fn_thread.daemon = True
    fn_thread.start()

def add_audio(audio_path, video_path):
    fn_thread = threading.Thread(target=add_audio,
                                 args=(full_path,))
    fn_thread.daemon = True
    fn_thread.start()

def record_audio(audio_path, video_path):
    fn_thread = threading.Thread(target=record_audio,
                                 args=(full_path,))
    fn_thread.daemon = True
    fn_thread.start()
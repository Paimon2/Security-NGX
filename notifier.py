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

import smtplib
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

json_obj = None

def init_notifier(j):
    global json_obj
    json_obj = j
    global server
   # server = smtplib.SMTP(j["notifications"]["email_server"], 
        #                  j["notifications"]["email_server_port"])
   # server.starttls()
    #server.login(j["notifications"]["acct_address"], j["notifications"]["acct_password"])

def send_notification(title, message, files=None):
   return
   fromaddr = json_obj["notifications"]["from_email"]
   toaddr = json_obj["notifications"]["to_email"]
   msg = MIMEMultipart()
   msg['Subject'] = title
   msg['From'] = fromaddr
   msg['To'] = toaddr
   msg.attach(MIMEText(message, 'plain'))
   for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)
   server.sendmail(fromaddr, \
                   toaddr, \
                   msg.as_string())

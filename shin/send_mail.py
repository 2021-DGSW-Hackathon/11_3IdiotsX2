import re
import smtplib
import picamera

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from PyQt5.QtCore import pyqtSlot


class SendMail:

    def __init__(self):
        self.smtp = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtp.starttls()
        self.smtp.login('3idiot.x2@gmail.com', 'eothrh11')

    def send_mail(self, recipient):
        if not re.match('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+$', recipient):
            print('불일치')
            return
        
        cam = picamera.PiCamera()
        cam.capture('./Warning.jpg')
        cam.close()

        msg = MIMEMultipart()
        msg['subject'] = 'Warning!!!'
        msg.attach(MIMEText('FBI Open up', 'plain'))

        fileSend = open('Warning.jpg', 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(fileSend.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= " + 'Warning.jpg')
        msg.attach(part)

        self.smtp.sendmail('Smart Home', recipient, msg.as_string())
        print('전송 성공')

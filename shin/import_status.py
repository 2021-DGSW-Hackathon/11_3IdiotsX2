import send_mail
import fingerprint
import sys
import board
import adafruit_dht
import RPi.GPIO as GPIO
import time
import picamera
from gpiozero import Motor

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

form_class = uic.loadUiType("status.ui")[0]
dhtDevice = adafruit_dht.DHT11(board.D4)

before_temp = 29
current_temp = 0
humidity = 0
cnt = 0
easterEggCnt = 0
chk = False
register_chk = False
fanWork = False
chkYours = False

class ChkDelay(QThread):
    timeout = pyqtSignal()
    
    def run(self):
        while True:
            self.timeout.emit()
            self.sleep(0.5)

class ChkFinger(QThread):
    global register_chk, chkYours
    mail = send_mail.SendMail()
    fingerPrint = fingerprint.FingerPrint()
        
    def run(self):
        global cnt, register_chk, chkYours
        while True:
            chkYours = self.fingerPrint.chkFinger()
            if chkYours == True:
                cnt = 0
            if chkYours == False and register_chk == False:
                print(cnt)
                cnt += 1
            elif register_chk == True:
                self.fingerPrint.enroll_finger()
                register_chk = False

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        GPIO.cleanup()
        self.setupUi(self)
        
        self.chk_delay = ChkDelay()
        self.chk_delay.start()
        self.chk_delay.timeout.connect(self.chk_status)
        self.chkFinger = ChkFinger()
        self.chkFinger.start()
        
        self.motor = Motor(forward = 20, backward = 21)

        self.mail = send_mail.SendMail()

        # self.finger = fingerprint.FingerPrint()
        self.fanButton.setText("Fan Work: " + str(fanWork))
        self.fanButton.clicked.connect(self.fanWorkFunc)
        self.CameraButton.clicked.connect(self.seeOutSide)
        self.registFingerPrint.clicked.connect(self.registFinger)

    def closeEvent(self, event):
        dhtDevice.exit()
        self.mail.smtp.close()

    @pyqtSlot()
    def chk_status(self):
        global cnt, chk, current_temp, humidity, fanWork, chkYours
        try:
            current_temp = dhtDevice.temperature
            humidity = dhtDevice.humidity
        except RuntimeError:
            pass
        except OverflowError:
            pass

        if cnt >= 5 and chk == False:
            chk = True
            self.mail.send_mail('shk052353@gmail.com')
            QMessageBox.information(self, "Warning!!!", "Who invade your house!!")
            cnt = 0
            chk = False
        
        if fanWork == True:
            self.fanMove(current_temp)
        else:
            self.motor.forward(speed=0.0)
        
        if chkYours == True and chk == False:
            chk =  True
            QMessageBox.information(self, "Warning!!", "Welcome Our Sweet Home!!")
            chkYours = False
            chk = False

        self.presentTime.setText(QTime.currentTime().toString())
        self.humidity.setText("Humidity: " + str(humidity) + "%")
        self.temp.setText("Temperature: " + str(current_temp) + "°C")

    def registFinger(self):
        global register_chk
        print("Complete!")
        register_chk = True
        # self.finger.enroll_finger()
    
    def fanWorkFunc(self):
        global fanWork
        if fanWork == True:
            fanWork = False
        else:
            fanWork = True
        self.fanButton.setText("Fan Work: " + str(fanWork))
    
    def fanMove(self, temp):
        if temp >= 30:
            self.motor.forward()
        elif temp >= 20 and temp < 30:
            self.motor.forward(speed = 0.3)
    
    def seeOutSide(self):
        cam = picamera.PiCamera()
        cam.start_preview()
        time.sleep(5)
        cam.stop_preview()
        cam.close()
    
    # def EasterEgg(self):
    #     global easterEggCnt
    #     if easterEggCnt >= 5:
    #         easterEggCnt = 0
    #         QMessageBox.information(self, "Easter Egg!", "All is well!!\n - Team 3 idiots -")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()

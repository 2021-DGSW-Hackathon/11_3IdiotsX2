import time
import serial
import adafruit_fingerprint


class FingerPrint:
    def __init__(self):
        self.FingerPrintSerial = serial.Serial("/dev/ttyUSB0", baudrate=57600)
        self.finger = adafruit_fingerprint.Adafruit_Fingerprint(self.FingerPrintSerial)
        self.cnt = 0
    
    def chkFinger(self):
        print("Waiting Image...")
        while self.finger.get_image() != adafruit_fingerprint.OK:
            pass
        print("Templating....")
        if self.finger.image_2_tz(1) != adafruit_fingerprint.OK:
            return False
        print("Searching...")
        if self.finger.finger_search() != adafruit_fingerprint.OK:
            return False
        return True
    
    def enroll_finger(self):
        for fingerimg in range(1, 3):
            if fingerimg == 1:
                print("Place finger on sensor...", end="", flush=True)
            else:
                print("Place same finger again...", end="", flush=True)

            while True:
                i = self.finger.get_image()
                if i == adafruit_fingerprint.OK:
                    print("Image Taken")
                    break
                if i == adafruit_fingerprint.OK:
                    print(".", end="", flush=True)
                elif i == adafruit_fingerprint.IMAGEFAIL:
                    print("Imaging error")
                    return False
                #else:
                #    print("Other error")
                #    return False

            print("Templating...", end="", flush=True)
            i = self.finger.image_2_tz(fingerimg)
            if i == adafruit_fingerprint.OK:
                print("Templated")
            else:
                if i == adafruit_fingerprint.IMAGEMESS:
                    print("Image too messy")
                elif i == adafruit_fingerprint.FEATUREFAIL:
                    print("Could not identify features")
                elif i == adafruit_fingerprint.INVALIDIMAGE:
                    print("Image invalid")
                else:
                    print("Other error")
                return False
            
            if fingerimg == 1:
                print("Remove finger")
                time.sleep(1)
                while i != adafruit_fingerprint.NOFINGER:
                    i = self.finger.get_image()

        print("Creating Model...", end="", flush=True)
        i = self.finger.create_model()
        if i == adafruit_fingerprint.OK:
            print("Created")
        else:
            if i == adafruit_fingerprint.ENROLLMISMATCH:
                print("Prints did not match")
            else:
                print("Other error")
            return False

        print("Storing Model #%d..." % self.cnt, end="", flush=True)
        i = self.finger.store_model(self.cnt)
        self.cnt += 1
        if i == adafruit_fingerprint.OK:
            print("Stored")
        else:
            if i == adafruit_fingerprint.BADLOCATION:
                print("Bad storage location")
            elif i == adafruit_fingerprint.FLASHERR:
                print("Flash storage error")
            else:
                print("Other error")
            return False
        return True
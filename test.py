#pır
from gpiozero import MotionSensor
from gpiozero import Buzzer
from gpiozero import LED
import time
import FaceRecognition
import FaceCapture
import FaceTrain
import numPad
import dispLcd
import threading
import pickle
from picamera2 import Picamera2

#Create an instance of the PiCamera2 object
cam = Picamera2()
redLed=LED(18)#RED
greenLed=LED(23)#green
yellowLed=LED(24)#yellow
## Initialize and start realtime video capture
# Set the resolution of the camera preview
cam.preview_configuration.main.size = (640, 480)
cam.preview_configuration.main.format = "RGB888"
cam.preview_configuration.controls.FrameRate=30
cam.preview_configuration.align()
cam.configure("preview")
cam.start()
pir = MotionSensor(14)
BIZBIZ=Buzzer(15)
isActive = False
def create_thread():
    return threading.Thread(target=timer,args=())

def ledControl(redFlag,yellowFlag,greenFlag):
    if redFlag:
        redLed.on()
    else:
        redLed.off()
    if yellowFlag:
        yellowLed.on()
    else:
        yellowLed.off()
    if greenFlag:
        greenLed.on()
    else:
        greenLed.off()
    
def timer():
    remaining = total
    temp=remaining
    while remaining > 0:
        end = time.time()
        remaining = int(total - (end-start))
        if remaining!=temp:
            print(remaining)
            temp=remaining
    shared = {"timer":remaining}
    dbfile = open('shared', 'wb')
    pickle.dump(shared, dbfile)
    dbfile.close()
def faceCheck():
    dispLcd.display("Face Detecting", "")
    return FaceRecognition.recognizeFace(cam)

def passwordCheck(userinf, id):
    userInp = numPad.inpStream(4)
    print(userInp)
    if userInp == "-1":
        BIZBIZ.on()
        dispLcd.clear()
        dispLcd.display("", "-------")                
        time.sleep(0.5)
        dispLcd.clear()
        ledControl(True, True, False)
    while userInp != "####" and userInp != "-1":
        if userInp == userinf[id][1]:
            isActive = False
            dispLcd.clear()
            dispLcd.display("", "password CORRECT")
            time.sleep(0.5)
            dispLcd.clear()
            BIZBIZ.off()
            ledControl(False, False, True)
            return isActive
        else:
            BIZBIZ.on()
            dispLcd.clear()
            dispLcd.display("", "password Incorrect")                
            time.sleep(0.5)
            dispLcd.clear()
            ledControl(True, True, False)
        dispLcd.clear()
        dispLcd.display(userinf[id][0], "")
        userInp = numPad.inpStream(4)
    return True
def addUser():
    dispLcd.clear()
    dispLcd.display("Enter password", "")
    userInp = numPad.inpStream(4)
    dispLcd.clear() 
    dispLcd.display("Look at the camera", "Detecting Face")
    FaceCapture.captureFaces(userInp, cam)           
    FaceTrain.trainFaces()
    dispLcd.clear()
    dispLcd.display("User added", "")
def activate():
    timer = 2
    while timer > 0:
        dispLcd.clear()
        text = "Active in" + str(timer) + "seconds..."
        dispLcd.display(text, "")
        timer -= 1
        time.sleep(1)
    dispLcd.clear()
    dispLcd.display("Alarm On", "")
    ledControl(True, False, False)
    return True

def checkUser(path):
#     with open(path, 'r') as fp:
#         userCount = len(fp.readlines())
#         fp.close();
#     userCount  -= 1
#     if userCount > 0:
#         return True
#     return False
    try:
        ledControl(True, True, False)
        time.sleep(0.5)
        dbfile = open('UserInfo', 'rb')
    except:
        dispLcd.clear()
        dispLcd.display("Add User First", "Press A")
        ledControl(False, False, True)
        return False
    dbfile.close()
    return True

t1 = create_thread()
t2 = create_thread()
ledThread = create_thread()
pirFlag=True
while True:
    #When alarm is active
    if isActive:
        
        print("active")
        if pirFlag:
            pir.wait_for_motion()
            pirFlag=False
        start = time.time()
        total = 20
        t1.start()
        userinf, id = faceCheck()
        total = 0
        t1.join()
        shared = {"timer":999}
        dbfile = open('shared', 'wb')
        pickle.dump(shared, dbfile)
        dbfile.close()
        t1 = create_thread()
        if id == -2:#if there is no such user ALERT!
            BIZBIZ.on()
            ledControl(True, False, False)            
        elif id == -1:
            isActive = False
            print("Add User First")
            dispLcd.clear()
            dispLcd.display("Add User First", "")
            ledControl(False, False, True)
        else:
            ledControl(True, True, False)
            dispLcd.clear()
            dispLcd.display(userinf[id][0], "")
            start = time.time()
            total = 20
            t2.start()
            isActive = passwordCheck(userinf, id)
            total = 0
            t2.join()
            shared = {"timer":999}
            dbfile = open('shared', 'wb')
            pickle.dump(shared, dbfile)
            dbfile.close()
            t2 = create_thread()
        pir.wait_for_no_motion()
    while not isActive:
        #inpStream = ''.join(numPad.inpStream(1))
        pirFlag=True
        ledControl(False, False, True)
        inpStream = input("Inactive Mode")
        if inpStream == "A":
            addUser()
            break
        elif inpStream == "#":
            if checkUser("dataset/UserInfo.txt"):
                isActive = activate()
        #Wait for numPad

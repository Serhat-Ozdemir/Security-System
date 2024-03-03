import cv2
import os
from picamera2 import Picamera2
import time
import pickle

# Constants
COUNT_LIMIT = 100
POS=(15,30)  #top-left
FONT=cv2.FONT_HERSHEY_COMPLEX #font type for text overlay
HEIGHT=1  #font_scale
TEXTCOLOR=(255,255,255)  #BGR- RED
BOXCOLOR=(120,250,250) #BGR- BLUE
WEIGHT=2  #font-thickness
FACE_DETECTOR=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
INFOPATH="dataset/UserInfo.txt"

def findId():
    try:
        dbfile = open('UserInfo', 'rb')
    except:
        return 0
    UserInfo = pickle.load(dbfile)
    id = len(UserInfo)
    dbfile.close()
    return id
#     with open(path, 'r') as fp:
#         id = len(fp.readlines())
#         fp.close();
#     id  -= 1
#     return id
def addUser(pswd):
    id = findId()
    password = ''.join(pswd)
    dbfile = open('UserInfo', 'rb')
    UserInfo = pickle.load(dbfile)
    dbfile.close()
    UserInfo[id] = ["User" +str(id),password]
    dbfile = open('UserInfo', 'wb')
    pickle.dump(UserInfo, dbfile)
    dbfile.close()
#     with open(path, 'a') as fp:
#         password = ''.join(pswd)
#         fp.write(str(id)+ "#User" +str(id)+"#"+str(password)+"\n")
#         fp.close()

# # For each person, enter one numeric face id


def captureFaces(pswd, cam):
#     #name = input('\n----Enter User-id and press <return>----')
#     cam=Picamera2()
#     ## Initialize and start realtime video capture
#     # Set the resolution of the camera preview
#     cam.preview_configuration.main.size = (640, 360)
#     cam.preview_configuration.main.format = "RGB888"
#     cam.preview_configuration.controls.FrameRate=30
#     cam.preview_configuration.align()
#     cam.configure("preview")
    cam.start()
    id = findId()
    name = "User"+str(id)
    print("\n [INFO] Initializing face capture. Look at the camera and wait!")
    count=0
    start = time.time()
    while True:
        end = time.time()
        remaining = (60 - (end-start))
        # Capture a frame from the camera
        frame=cam.capture_array()
        # Display count of images taken
        cv2.putText(frame,'Count:'+str(int(count)),POS,FONT,HEIGHT,TEXTCOLOR,WEIGHT)

        # Convert frame from BGR to grayscale
        frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Create a DS faces- array with 4 elements- x,y coordinates (top-left corner), width and height
        faces = FACE_DETECTOR.detectMultiScale( # detectMultiScale has 4 parameters
                frameGray,      # The grayscale frame to detect
                scaleFactor=1.1,# how much the image size is reduced at each image scale-10% reduction
                minNeighbors=10, # how many neighbors each candidate rectangle should have to retain it
                minSize=(50, 50)# Minimum possible object size. Objects smaller than this size are ignored.
        )
        for (x,y,w,h) in faces:
            # Create a bounding box across the detected face
            cv2.rectangle(frame, (x,y), (x+w,y+h), BOXCOLOR, 3) # 5 parameters - frame, topleftcoords,bottomrightcooords,boxcolor,thickness
            # if dataset folder doesnt exist create:
            if not os.path.exists("dataset/" + name):
                os.makedirs("dataset/" + name)
            # Save the captured bounded-grayscaleimage into the datasets folder only if the same file doesn't exist
            file_path = os.path.join("dataset/" + name, f"{id}.{count}.jpg")
            cv2.imwrite(file_path, frameGray[y:y+h, x:x+w])
            count += 1;
        # Display the original frame to the user
        cv2.imshow('FaceCapture', frame)
        # Wait for 30 milliseconds for a key event (extract sigfigs) and exit if 'ESC' or 'q' is pressed
        key = cv2.waitKey(100) & 0xff
        # Checking keycode
        if key == 27:  # ESCAPE key
            break
        elif int(remaining) == 0:  # Space key
            break
        if count >= COUNT_LIMIT: # Take COUNT_LIMIT face samples and stop video capture
            print("\n [INFO] Exiting Program and cleaning up stuff")
            addUser(pswd)
            break

    # Release the camera and close all windows

    cv2.destroyAllWindows()
import cv2
import os
import numpy as np
from picamera2 import Picamera2
import time
import pickle

#Parameters
id = 0
font = cv2.FONT_HERSHEY_COMPLEX
height=1
boxColor=(200,250,50)      #BGR- GREEN
nameColor=(255,255,255) #BGR- WHITE
confColor=(255,255,0)   #BGR- TEAL1

face_detector=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()


#List of names with ids
def getUserList():
#     users = {}
#     with open("dataset/UserInfo.txt", 'r') as fp:
#         fp.readline()
#         while True:
#             content=fp.readline()
#             if content!="":
#                 info = content.split('#')
#                 users[int(info[0])] = [info[1], info[2].replace('\n','')]
#             if not content:
#                 break
#     fp.close()
#     return users
    try:
        dbfile = open('UserInfo', 'rb')
    except:
        return None
    UserInfo = pickle.load(dbfile)
    dbfile.close()
    return UserInfo

# #Create an instance of the PiCamera2 object
# cam = Picamera2()
# ## Initialize and start realtime video capture
# # Set the resolution of the camera preview
# cam.preview_configuration.main.size = (640, 360)
# cam.preview_configuration.main.format = "RGB888"
# cam.preview_configuration.controls.FrameRate=30
# cam.preview_configuration.align()
# cam.configure("preview")
# cam.start()

def recognizeFace(cam):
    remaining = 999
    try:
        recognizer.read('trainer/trainer.yml')
    except:
        print("Add User First")
        return None, -1
    users = getUserList()
    while True:
        # Capture a frame from the camera
        frame=cam.capture_array()
        #Convert fram from BGR to grayscale
        frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #Create a DS faces- array with 4 elements- x,y coordinates top-left corner), width and height
        faces = face_detector.detectMultiScale(
                frameGray,      # The grayscale frame to detect
                scaleFactor=1.1,# how much the image size is reduced at each image scale-10% reduction
                minNeighbors=10, # how many neighbors each candidate rectangle should have to retain it
                minSize=(50, 50)# Minimum possible object size. Objects smaller than this size are ignored.
                )
        for(x,y,w,h) in faces:
            namepos=(x+5,y-5) #shift right and up/outside the bounding box from top
            confpos=(x+5,y+h-5) #shift right and up/intside the bounding box from bottom
            #create a bounding box across the detected face
            cv2.rectangle(frame, (x,y), (x+w,y+h), boxColor, 2) #5 parameters - frame, topleftcoords,bottomrightcooords,boxcolor,thickness
            #recognizer.predict() method takes the ROI as input and
            #returns the predicted label (id) and confidence score for the given face region.
            id, confidence = recognizer.predict(frameGray[y:y+h,x:x+w])
            #If confidence is less than 100, it is considered a perfect match
            #Display name and confidence of person who's face is recognized
            print(users)
            name = users[id][0]
            
            cv2.putText(frame, name, namepos, font, height, nameColor, 2)
            cv2.putText(frame, str(confidence), confpos, font, height, confColor, 1)
            if confidence > 40:
                #confidence = f"{confidence:.0f}%"
                cv2.destroyAllWindows()
                return users, id
        # Display realtime capture output to the user
        cv2.imshow('Raspi Face Recognizer',frame)
        # Wait for 30 milliseconds for a key event (extract sigfigs) and exit if 'ESC' or 'q' is pressed
        key = cv2.waitKey(100) & 0xff
        #Checking keycode
        try:
            dbfile = open('shared', 'rb')
            shared = pickle.load(dbfile)
            remaining = shared['timer']
        except:
            pass
        if int(remaining) <= 0:  # ESCAPE key
            cv2.destroyAllWindows()
            dbfile = open('shared', 'wb')
            shared['timer'] = 999
            pickle.dump(shared, dbfile)
            dbfile.close()
            print("olduuuu!")
            return None, -2

#     # Release the camera and close all windows
#     print("\n [INFO] Exiting Program and cleaning up stuff")
#     print(names)
#     cam.stop()
#     cv2.destroyAllWindows()
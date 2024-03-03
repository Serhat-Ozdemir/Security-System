import RPi.GPIO as GPIO
import time
import dispLcd
import pickle

# Set the Row Pins
ROW_1 = 17
ROW_2 = 27
ROW_3 = 22
ROW_4 = 10

# Set the Column Pins
COL_1 = 9
COL_2 = 11
COL_3 = 5
COL_4 = 6

GPIO.setwarnings(False)
# BCM numbering
GPIO.setmode(GPIO.BCM)

# Set Row pins as output
GPIO.setup(ROW_1, GPIO.OUT)
GPIO.setup(ROW_2, GPIO.OUT)
GPIO.setup(ROW_3, GPIO.OUT)
GPIO.setup(ROW_4, GPIO.OUT)

# Set column pins as input and Pulled up high by default
GPIO.setup(COL_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(COL_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(COL_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(COL_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# function to read each row and each column
def readRow(line, characters, arr):
    GPIO.output(line, GPIO.LOW)
    if(GPIO.input(COL_1) == GPIO.LOW):
        if len(arr)!=0 and characters[0] == "*":
            arr.pop()
            temp=arr.copy()#OLDU
            temp.append(' ')
            dispLcd.display("", temp)
        elif characters[0] != "*":
            arr.append (characters [0])
            dispLcd.display("", arr)
            print(arr)
    if(GPIO.input(COL_2) == GPIO.LOW):
        arr.append (characters [1])
        dispLcd.display("", arr)
        print(arr)
    if(GPIO.input(COL_3) == GPIO.LOW):
        arr.append (characters [2])
        dispLcd.display("", arr)
        print(arr)
    if(GPIO.input(COL_4) == GPIO.LOW):
        arr.append (characters [3])
        dispLcd.display("", arr)
        print(arr)
    GPIO.output(line, GPIO.HIGH)
def inpStream(length):
    remaining = 999
    # Endless loop by checking each row 
    try:
        print("Press buttons on your keypad. Ctrl+C to exit.")
        inp = []
        while len(inp) < length:
            readRow(ROW_1, ["1","2","3","A"], inp)
            readRow(ROW_2, ["4","5","6","B"], inp)
            readRow(ROW_3, ["7","8","9","C"], inp)
            readRow(ROW_4, ["*","0","#","D"], inp)
            time.sleep(0.2) # adjust this per your own setup
            try:
                dbfile = open('shared', 'rb')
                shared = pickle.load(dbfile)
                remaining = shared['timer']
                
            except:
                pass
            if int(remaining) <= 0:  # ESCAPE key 
                dbfile = open('shared', 'wb')
                shared['timer'] = 999
                pickle.dump(shared, dbfile)
                dbfile.close()
                print("olduuuu!")
                return '-1'
        return ''.join(inp)
        
    except KeyboardInterrupt:
        print("\nKeypad Application Interrupted!")
        GPIO.cleanup()
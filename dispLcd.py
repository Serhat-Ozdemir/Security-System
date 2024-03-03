import drivers
import time
from subprocess import check_output

displayer = drivers.Lcd()
def clear():
    displayer.lcd_clear()
def display(text1, text2):
    try:
        password = ''.join(text2)
        displayer.lcd_display_string(text1, 1)  # Display the IP address on the second line
        displayer.lcd_display_string(password, 2)  # Display the IP address on the second line
        time.sleep(0.2)
    except KeyboardInterrupt:
        # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
        print("Cleaning up!")
        sleep(.4)
        displayer.lcd_clear()

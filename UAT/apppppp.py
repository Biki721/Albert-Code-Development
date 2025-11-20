import time
import pyautogui
import random
 
pyautogui.FAILSAFE = False
 
while True:
    # Move the mouse to a specific position on the screen
    # pyautogui.moveTo(random.randint(100,200), random.randint(100,200))    
    pyautogui.click()
 
 
 
    # Wait for 10 seconds
    time.sleep(5)
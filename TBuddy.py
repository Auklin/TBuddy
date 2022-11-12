import threading
import os
import time
import PIL
import win32gui #py -m pip install win32gui
import pyautogui #py -m pip install pyautogui
import win32api
import win32.lib.win32con as win32con
from pynput import mouse
from pynput import keyboard #py -m pip install keyboard 
import PySimpleGUI as gui

#cd "Documents\My Games\Terraria"
#pyinstaller --onefile "TBuddy.py"

keepRunning = False
mouseController = mouse.Controller()
keyboardController = keyboard.Controller()
pressedCords = (0,0)
releasedCords = (0,0)
lastKeySelected = '1'
currentLoadout = 1
clickDelay = 0
quickUseMiddleMouse = '4'
quickUseBackMouse = '0'
quickUseForwardMouse = '9'
fishingType = "Advanced"
advancedFishTolerance = 75
loadoutSwapToggle = False
basicFishDelay = 3
configMenuOpen = False

print("Thanks for using TBuddy! Press F9 to start the configuration menu\n"+
      "Press the v key to switch loadouts\n"+
      "Press mouse buttons to quickly use other hotbar items\n"+
      "Press the right Alt key to begin autofishing\n\n"+
      "Advanced Fishing Instructions:\n"+
      "\t1) Click where you would like to cast, hold the click / do no unclick\n"
      "\t2) Move your mouse over your bobber, unclick on your bobber on a pixel that isn't change color\n"+
      "\t3) Press right Alt key, watch to verify functionality\n"+
      "\t4) AFK\n"+
      "\t5) Use movement keys to cancel\n"
      "Notes: The script works by constantly checking for a change on the pixel you unclicked on.\n"+
      "UI elements, effects, rain, splashes, knockback and enemies can trigger false positives.\n"+
      "Low lighting may require you to lower tolerance levels in the config, it is usually easier to just light up the area")

# Experimental, trying to autofish without window being active
def windowedLeftClick(x= None, y=None):
    
    global pressedCords, releasedCords
    # pressedCords = (0,0)
    (px,py) = pressedCords
    # releasedCords = (0,0)
    (rx,ry) = releasedCords
    
    hWnd = win32gui.FindWindow(None, "Terraria")
    print("terraria?:" ,hWnd)
    
    left_top_x, left_top_y, *useless_position = win32gui.GetWindowRect(hWnd) # get the position of window you gave.
    
    pos_in_window_x, pos_in_window_y = (px - left_top_x), (py - left_top_y)
    global keepRunning
    keepRunning = True
    f = 1
    while keepRunning:
        lParam = win32api.MAKELONG(pos_in_window_x, pos_in_window_y)
        print(lParam, f, f)
        win32api.PostMessage(hWnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        wait(0.2)
        win32api.PostMessage(hWnd, win32con.WM_LBUTTONUP, None, lParam)
        f=f+1
    
# Slow left click with optional coordinates
def leftClickSlow(x= None, y=None):
    if (x and y):
        pyautogui.mouseDown(x,y)
        wait(0.3)
        pyautogui.mouseUp(x,y)
    else:
        mouseController.press(mouse.Button.left)
        wait(0.3)
        mouseController.release(mouse.Button.left)
    wait(0.3)
    
# Left click with optional coordinates
def leftClick(x= None, y=None):
    if (x and y):
        pyautogui.mouseDown(x,y)
        wait(0.05+clickDelay)
        pyautogui.mouseUp(x,y)
    else:
        mouseController.press(mouse.Button.left)
        wait(0.3+clickDelay)
        mouseController.release(mouse.Button.left)
    wait(0.3+clickDelay)
       
# Delay for use in between key presses
def wait(x):
    time.sleep(x)
    
# Press a key with a needed delay
def pressKey(key):
    keyboardController.press(key)
    wait(0.05+clickDelay)
    keyboardController.release(key)

# Quickly use a hotbar key, then return to last selected hotbar item
def quickUse(key):
    global lastKeySelected
    lk = lastKeySelected
    
    pressKey(key)
    
    mouseController.press(mouse.Button.left)
    wait(0.05+clickDelay)
    mouseController.release(mouse.Button.left)
    
    pressKey(lk)
    
#old basic fishing script
def basicFish():
    global keepRunning, basicFishDelay
    keepRunning = True
    while keepRunning:
        print("Starting Loop")
        leftClickSlow()
        print("Waiting ",basicFishDelay, " seconds")
        wait(basicFishDelay)
        leftClickSlow()
        print("Catching fish")
        wait(.4)

# Pixel tracking fishing script
def advancedFish():
    print("Starting Advanced Fish")
    
    global pressedCords, releasedCords, advancedFishTolerance
    (px,py) = pressedCords
    (rx,ry) = releasedCords
    t = advancedFishTolerance #Tolerance for pixel changes
    catchCount = 0
    
    leftClickSlow()
    
    while keepRunning:
        leftClickSlow(px,py)
        wait(1)
        if not keepRunning:
            break
        rgb = get_pixel_colour(rx,ry)
        (r,g,b) = rgb
        while keepRunning:
            xrgb = get_pixel_colour(rx,ry)
            (xr,xg,xb) = xrgb
            #print(r,g,b,xr,xg,xb,' at ',rx,ry)
            if ( (r-t < xr < r+t) and (g-t < xg < g+t) and (b-t < xb < b+t)):
                continue
            catchCount+=1
            print(f"The bobber pixel changed! Reeling in #{catchCount}")
            break
        if not keepRunning:
            break
        leftClickSlow()
        wait(.5)
    
# Gets pixel color of provided x,y coordinates
def get_pixel_colour(i_x, i_y):
	i_desktop_window_id = win32gui.GetDesktopWindow()
	i_desktop_window_dc = win32gui.GetWindowDC(i_desktop_window_id)
	long_colour = win32gui.GetPixel(i_desktop_window_dc, i_x, i_y)
	i_colour = int(long_colour)
	win32gui.ReleaseDC(i_desktop_window_id,i_desktop_window_dc)
	return (i_colour & 0xff), ((i_colour >> 8) & 0xff), ((i_colour >> 16) & 0xff)

def userConfiguration():
    configuring = True
    global quickUseMiddleMouse, quickUseForwardMouse, quickUseBackMouse, loadoutSwapToggle, fishingType, advancedFishTolerance, basicFishDelay, clickDelay, configMenuOpen
    configMenuOpen = True
    while (configuring):
        x = input("Press key (then press enter) to configure settings: "+
                  f"\n1: Change hotbar key associated with middle mouse click, current is {quickUseMiddleMouse}"+
                  f"\n2: Change hotbar key associated with forward mouse click, current is {quickUseForwardMouse}"+
                  f"\n3: Change hotbar key associated with back mouse click, current is {quickUseBackMouse}"+
                  f"\n4: Toggle v key loadout swap to only cycle loadout 1 and 2, toggle is currently set to {loadoutSwapToggle}"+
                  f"\n5: Toggle Autofishing as Advanced or Basic, currently using {fishingType}"+
                  f"\n6: Changed Avanced fishing pixel change tolerance, currently set to {advancedFishTolerance}"+
                  f"\n7: Change delay/ time of Basic auto fish, currently set to {basicFishDelay}"+
                  f"\n8: Change delay of autoclicking (useful for older computers), currently set to {clickDelay} seconds"+
                  f"\n9: Exit\n")
        if (x=='1'):
            
            x = input("Give a number key for middle mouse, type 'disable' to disable the functionality: \n")
            if x.isnumeric() and len(x) == 1:
                quickUseMiddleMouse = x
            if x == 'disable':
                 quickUseMiddleMouse = False
        elif (x=='2'):
            x = input("Give a number key for forward mouse, type 'disable' to disable the functionality: \n")
            if x.isnumeric() and len(x) == 1:
                quickUseForwardMouse = x  
            if x == 'disable':
                 quickUseForwardMouse = False
        elif (x=='3'):
            x = input("Give a number key for back mouse, type 'disable' to disable the functionality: \n")
            if x.isnumeric() and len(x) == 1:
                quickUseBackMouse = x
            if x == 'disable':
                 quickUseBackMouse = False
        elif (x=='4'):
            loadoutSwapToggle = not loadoutSwapToggle
        elif (x=='5'):
            if fishingType == 'Advanced':
                fishingType = 'Basic'
            elif fishingType == 'Basic':
                fishingType = 'Advanced'
        elif (x=='6'):
            x = input("Enter a tolerance between 0 and 255: \n")
            try:
                if (0 < int(x) <= 255):
                    advancedFishTolerance = int(x)
                print(f"Tolerance is now {advancedFishTolerance}")
            except:
                print ('Please enter a valid number, returning to menu')
        elif (x=='7'):
            x = input("Enter a value greater than 1 and less than 10: \n")
            try:
                if (1 <= float(x) <= 10):
                    basicFishDelay = float(x)
                print('Basic fishing delay is now ',basicFishDelay)
            except:
                print ('Invalid input')
        elif (x=='8'):
            x = input("Enter a value for click delay. 0 is default, 3 is too high: \n")
            try:
                if (0 <= float(x) <= 3):
                    clickDelay = float(x)
                print('Basic fishing delay is now ',clickDelay)
            except:
                print ('Invalid input')
            
        elif (x=='9'):
            configuring = False
            print("Exiting Menu")
        else:
            print('Input was not valid')
            
    configMenuOpen = False; 
    

# print(pyautogui.position().x)

# Detects key press
def on_press(key):
    global keepRunning, currentLoadout
    
    # If non-alphanumeric key:
    if (isinstance(key,keyboard.Key)):
        match key:
            case keyboard.Key.f1:
                currentLoadout = 1
            case keyboard.Key.f2:
                currentLoadout = 2
            case keyboard.Key.f3:
                currentLoadout = 3
            case keyboard.Key.f9:
                global configMenuOpen
                if not configMenuOpen:
                    thread2 = threading.Thread(target = userConfiguration, args=())
                    thread2.start()
            case keyboard.Key.alt_gr:
                keepRunning = True
                if fishingType == 'Advanced':
                    thread2 = threading.Thread(target = advancedFish, args=())
                elif fishingType == 'Basic':
                    thread2 = threading.Thread(target = basicFish, args=())
                thread2.start()
                
    # If alphanumeric key
    elif (isinstance(key,keyboard.KeyCode)):
        global lastKeySelected
        match key:
            case keyboard._base.KeyCode(char="w"):
                keepRunning = False
            case keyboard._base.KeyCode(char="a"):
                keepRunning = False
            case keyboard._base.KeyCode(char="s"):
                keepRunning = False
            case keyboard._base.KeyCode(char="d"):
                keepRunning = False
            case keyboard._base.KeyCode(char="v"): 
                global loadoutSwapToggle
                match currentLoadout:
                    case 1:
                        pressKey(keyboard.Key.f2)
                        currentLoadout = 2
                    case 2:
                        if loadoutSwapToggle:
                            pressKey(keyboard.Key.f1)
                            currentLoadout = 1
                        else:
                            pressKey(keyboard.Key.f3)
                            currentLoadout = 3
                    case 3:
                        pressKey(keyboard.Key.f1)
                        currentLoadout = 1
            
            # Detect hotbar keys
            case keyboard._base.KeyCode(char="1"):
                lastKeySelected = '1'
            case keyboard._base.KeyCode(char="2"):
                lastKeySelected = '2'
            case keyboard._base.KeyCode(char="3"):
                lastKeySelected = '3'
            case keyboard._base.KeyCode(char="4"):
                lastKeySelected = '4'
            case keyboard._base.KeyCode(char="5"):
                lastKeySelected = '5'
            case keyboard._base.KeyCode(char="6"):
                lastKeySelected = '6'
            case keyboard._base.KeyCode(char="7"):
                lastKeySelected = '7'
            case keyboard._base.KeyCode(char="8"):
                lastKeySelected = '8'
            case keyboard._base.KeyCode(char="9"):
                lastKeySelected = '9'
    
# Detects mouse clicks    
def on_click(x, y, button, pressed):
    if pressed:
        if button == mouse.Button.left:
            global pressedCords
            pressedCords = (x,y)                
        elif button == mouse.Button.x1 and quickUseBackMouse:
            thread2 = threading.Thread(target = quickUse, args=(quickUseBackMouse)) # Change any of these to alter behavior of quickUse
            thread2.start()
        elif button == mouse.Button.x2 and quickUseForwardMouse:
            thread2 = threading.Thread(target = quickUse, args=(quickUseForwardMouse))
            thread2.start()
        elif button == mouse.Button.middle and quickUseMiddleMouse:
            thread2 = threading.Thread(target = quickUse, args=(quickUseMiddleMouse))
            thread2.start()
    else:
        global releasedCords
        releasedCords = (x,y)
        
# Keyboard and Mouse listener handling
mlistener = mouse.Listener(
    on_click=on_click)
mlistener.start()

klistener = keyboard.Listener(
    on_press=on_press)
klistener.start()

klistener.join() 
mlistener.join()
# kblistener = keyboard.Listener(on_press=on_press)
# kblistener.start()  # start to listen on a separate thread
# kblistener.join() # remove if main thread is polling self.keys
#/usr/bin/python

# An electronic piggy bank that sorts and securely stores your coins.

# It uses a Raspberry Pi, an Arduino, a Coin Acceptor, the Adafruit LCD Shield, 
# and 3 LEGO Mindstorms motors connected to an NXT.

# Both the NXT and Arduino are connected to a USB hub connected to the Raspberry Pi

# Adafruit's Raspberry Pi Python Library can be found at:
# https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

# nxt-python is used to communicate with the NXT. It can be found at:
# https://code.google.com/p/nxt-python/

from time import sleep
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
import decimal, serial, nxt.locator
from nxt.motor import *

# Initialize the LCD plate
lcd = Adafruit_CharLCDPlate()
lcd.begin(16,2)

# Disable cursor and clear display
lcd.noCursor()
lcd.noBlink()
lcd.clear()

# Establish serial connection with Arduino
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# Functions to easily write to LCD
def display(msg, col, row, clear=False, backlight=-1):
    if clear: lcd.clear()
    if backlight!=-1: lcd.backlight(backlight)
    lcd.setCursor(col, row)
    lcd.message(msg)
    
def displayError(msg):
    lcd.clear()
    lcd.setCursor(0,0)
    lcd.backlight(lcd.RED)
    lcd.message(msg)
    
def displayAmount():
    lcd.setCursor(7,1)
    lcd.message('$' + str(amount))

def displayMainScreen(showTotals=False):
    lcd.clear()
    lcd.setCursor(0,0)
    # Write message to LCD
    if not showTotals:
        lcd.message("Alex's Piggy\nBank")
        displayAmount()
    else:
        lcd.message("Total:"+str(numQuarters+numDimes+numNickels+numPennies))
        lcd.setCursor(10,0)
        lcd.message("Q: "+str(numQuarters))
        lcd.setCursor(0,1)
        lcd.message("D:"+str(numDimes))
        lcd.setCursor(5,1)
        lcd.message("N:"+str(numNickels))
        lcd.setCursor(11,1)
        lcd.message("P:"+str(numPennies))
    
    # Set LCD backlight to green
    lcd.backlight(lcd.GREEN)
    sleep(.5)

# Function that writes the number of a particular kind of coin to LCD during OPENDOOR screen
def displayCurrentCoinTotal():
    display("AUTHENTICATED",0,0,True,lcd.ON)
    
    if position=="QUARTER":
        if numQuarters==1: display("1 QUARTER",0,1)
        else: display(str(numQuarters)+" QUARTERS",0,1)
    elif position=="DIME":
        if numDimes==1: display("1 DIME",0,1)
        else: display(str(numDimes)+" DIMES",0,1)
    elif position=="NICKEL":
        if numNickels==1: display("1 NICKEL",0,1)
        else: display(str(numNickels)+" NICKELS",0,1)
    elif position=="PENNY":
        if numPennies==1: display("1 PENNY",0,1)
        else: display(str(numPennies)+" PENNIES",0,1)

# Function that updates amount variable when number of a particular kind of coin changes
def recalculateTotalAmount():
    global amount
    amount = decimal.Decimal('0.00')
    amount += decimal.Decimal('0.25') * decimal.Decimal(numQuarters)
    amount += decimal.Decimal('0.10') * decimal.Decimal(numDimes)
    amount += decimal.Decimal('0.05') * decimal.Decimal(numNickels)
    amount += decimal.Decimal('0.01') * decimal.Decimal(numPennies)

# Function that writes new amount, position,  num coins data to text file
def updateDataFile():
    try:
        f = open("data.txt", 'w')
    except IOError:
        displayError("Error opening\ndata.txt")
        exit()
    
    f.seek(0)
    f.write(str(amount))
    f.write('\n')
    f.write(position.rstrip('\n'))
    f.write('\n')
    f.write(str(numQuarters))
    f.write('\n')
    f.write(str(numDimes))
    f.write('\n')
    f.write(str(numNickels))
    f.write('\n')
    f.write(str(numPennies))
    f.close()
    
# NXT Brick object
b = None
    
# Function that connects to NXT
def connectToNXT():
    global b
    if b==None:
        try:
            b = nxt.locator.find_one_brick()
        except nxt.locator.BrickNotFoundError: 
            displayError("Can't connect to\nNXT")
            time.sleep(5)
            currentScreen = "Main"
            displayMainScreen()
    
# Constants for NXT control
M_LOCK = PORT_A
M_FEED = PORT_B
M_ROTATE = PORT_C

LOCK_SPEED = 70
FEED_SPEED = 25
ROTATE_SPEED = 70

LOCK_DISTANCE = 160
FEED_DISTANCE = 27

# Constant for fingerprint accepted status
FINGERPRINT_AUTHENTICATED = "THE EAGLE HAS LANDED"


# Try reading amount and position from file
try:
    f = open("data.txt", 'r')
except IOError:
    displayError("Error opening\ndata.txt")
    exit()

# Write message to LCD at 0,0 - Clear LCD, Green Backlight
display("Alex's Piggy\nBank",0,0,True,lcd.GREEN)

f.seek(0)
amount = f.readline()
position = f.readline()
numQuarters = f.readline()
numDimes = f.readline()
numNickels = f.readline()
numPennies = f.readline()

# Set flag to write to file if contents are empty
shouldWrite = False
if position == "":
    position = "QUARTER"
    shouldWrite = True

position = position.rstrip('\n')

try:
    amount = decimal.Decimal(amount)
    numQuarters = int(numQuarters)
    numDimes = int(numDimes)
    numNickels = int(numNickels)
    numPennies = int(numPennies)
except (decimal.InvalidOperation, ValueError):
    amount = decimal.Decimal('0.00')
    numQuarters = numDimes = numNickels = numPennies = 0
    shouldWrite = True

f.close()
if shouldWrite: # Write default values to file
    updateDataFile()

displayAmount()
    
currentScreen = "Main"

# Array of coin values and names
coins = (('QUARTER','0.25'), ('DIME','0.10'), ('NICKEL','0.05'), ('PENNY','0.01'))

# Main program loop
while True:
    try:
        # From Main Screen, user can any of the buttons
        # Select goes to Insert screen; Right ends program
        # Left enters authenticate mode
        # Up shows # of each type of coin; Down shows amount
        if currentScreen == "Main":
            if lcd.buttonPressed(lcd.SELECT):
                display("Please insert\ncoins",0,0,True,lcd.TEAL)
                displayAmount()
                currentScreen = "Insert"
                connectToNXT()
                sleep(.5)
            elif lcd.buttonPressed(lcd.RIGHT):
                raise KeyboardInterrupt
            elif lcd.buttonPressed(lcd.UP):
                displayMainScreen(True)
            elif lcd.buttonPressed(lcd.DOWN):
                displayMainScreen()
            elif lcd.buttonPressed(lcd.LEFT):
                display("Authenticate\nyourself",0,0,True,lcd.YELLOW)
                currentScreen = "Authenticate"
                
                text = ""
                ser.flushInput()
                ser.write('F')
            #elif lcd.buttonPressed(lcd.LEFT):
            #    connectToNXT()
            #    display("Maintenance Mode", 0, 0, True, lcd.RED)
            #    currentScreen = "Maintenance"
            #    sleep(.5)
        
        # From insert screen, user either enters coins or presses right to
        # go back to Main screen
        elif currentScreen == "Insert":
            if lcd.buttonPressed(lcd.RIGHT):
                updateDataFile()
                displayMainScreen()
                currentScreen = "Main"
            
            # Read serial data from Arduino - name of coin
            text = ""
            text = ser.readline()
            
            for c in coins:
                if text.find(c[0])!=-1:
                    # Output coin name and number of that type of coin
                    display(c[0],0,0,True,lcd.VIOLET)
                    if c[0]=='QUARTER':
                        numQuarters += 1
                        if numQuarters==1: display("1 coin",8,0)
                        elif numQuarters<100: display(str(numQuarters)+" coins",8,0)
                        else: display(str(numQuarters)+"coins",8,0)
                    elif c[0]=='DIME':
                        numDimes += 1
                        if numDimes==1: display("1 coin",8,0)
                        elif numDimes<100: display(str(numDimes)+" coins",8,0)
                        else: display(str(numDimes)+" coins",7,0)
                    elif c[0]=='NICKEL':
                        numNickels += 1
                        if numNickels==1: display("1 coin",8,0)
                        elif numNickels<100: display(str(numNickels)+" coins",8,0)
                        else: display(str(numNickels)+" coins",7,0)
                    elif c[0]=='PENNY':
                        numPennies += 1
                        if numPennies==1: display("1 coin",8,0)
                        elif numPennies<100: display(str(numPennies)+" coins",8,0)
                        else: display(str(numPennies)+" coins",7,0)
                    amount += decimal.Decimal(c[1])
                    displayAmount()
                    nextPlace = c[0]
                    try:
                        m_rotate = Motor(b, M_ROTATE)
                        # Rotate base if the inserted coin doesn't match with the
                        # coin pile on the base
                        if position!=nextPlace:
                            if position=="QUARTER":
                                if nextPlace=="DIME": m_rotate.turn(ROTATE_SPEED, 90)
                                elif nextPlace=="NICKEL": m_rotate.turn(ROTATE_SPEED, 180)
                                elif nextPlace=="PENNY": m_rotate.turn(-(ROTATE_SPEED), 90)
                            elif position=="DIME":
                                if nextPlace=="QUARTER": m_rotate.turn(-(ROTATE_SPEED), 90)
                                elif nextPlace=="NICKEL": m_rotate.turn(ROTATE_SPEED, 90)
                                elif nextPlace=="PENNY": m_rotate.turn(ROTATE_SPEED, 180)
                            elif position=="NICKEL":
                                if nextPlace=="QUARTER": m_rotate.turn(ROTATE_SPEED, 180)
                                elif nextPlace=="DIME": m_rotate.turn(-(ROTATE_SPEED), 90)
                                elif nextPlace=="PENNY": m_rotate.turn(ROTATE_SPEED, 90)
                            elif position=="PENNY":
                                if nextPlace=="QUARTER": m_rotate.turn(ROTATE_SPEED, 90)
                                elif nextPlace=="DIME": m_rotate.turn(ROTATE_SPEED, 180)
                                elif nextPlace=="NICKEL": m_rotate.turn(-(ROTATE_SPEED), 90)
                            sleep(.25)    
                        
                        position = nextPlace        
                        m_feed = Motor(b, M_FEED)
                        m_feed.turn(FEED_SPEED, FEED_DISTANCE)
                        sleep(1)
                        m_feed.turn(-(FEED_SPEED), FEED_DISTANCE)
                        display("Please insert\ncoins",0,0,True,lcd.TEAL)
                        displayAmount()
                    except:
                        # If the NXT turns off on its own or the motors are blocked,
                        # throw error message and save changes to data file before exiting
                        displayError("NXT has turned\noff / is blocked")
                        updateDataFile()
                        exit()
        
        # Uncomment for Maintenance mode which allows for fine tuning of base position
        #elif currentScreen == "Maintenance":
        #    if lcd.buttonPressed(lcd.LEFT):
        #        m_rotate = Motor(b, M_ROTATE)
        #        m_rotate.turn(ROTATE_SPEED, 10, False)
        #        sleep(.5)
        #    elif lcd.buttonPressed(lcd.RIGHT):
        #        m_rotate = Motor(b, M_ROTATE)
        #        m_rotate.turn(-(ROTATE_SPEED), 10, False)
        #        sleep(.5)
        #    elif lcd.buttonPressed(lcd.SELECT):
        #        updateDataFile()
        #        currentScreen = "Main"
        #        displayMainScreen()
        elif currentScreen == "Authenticate":
            if lcd.buttonPressed(lcd.RIGHT):
                currentScreen = "Main"
                displayMainScreen()
            
            text = ser.readline()
            
            # Test without fingerprint sensor
            #time.sleep(2)
            #text = FINGERPRINT_AUTHENTICATED
            
            if text.find(FINGERPRINT_AUTHENTICATED)!=-1:
                currentScreen = "OPENDOOR"
                display("AUTHENTICATED\nOpening Door...",0,0,True,lcd.ON)
                ser.flushInput()
                ser.write('C')
                connectToNXT()
                sleep(1)
                # Continue as long as NXT is on
                if b!=None:
                    m_lock = Motor(b, M_LOCK)
                    m_lock.turn(-(LOCK_SPEED), LOCK_DISTANCE)
                    m_rotate = Motor(b, M_ROTATE)
                    # Allow user fine adjustment
                    m_rotate.idle()
                    displayCurrentCoinTotal()
                else:
                    currentScreen = "Main"
        
        # From OPENDOOR screen, user can:
        # Left: Rotate to next coin; Up: Increase # of each coin
        # Down: Decrease # of each coin; Right: Return to main screen (Lock door)
        elif currentScreen == "OPENDOOR":
            if lcd.buttonPressed(lcd.RIGHT):
                updateDataFile()
                display("Locking Door...",0,0,True,lcd.YELLOW)
                sleep(1.5)
                connectToNXT()
                # Continue as long as NXT is on
                if b!=None:
                    m_lock = Motor(b, M_LOCK)
                    m_lock.turn(LOCK_SPEED, LOCK_DISTANCE)
                currentScreen = "Main"
                displayMainScreen()
            elif lcd.buttonPressed(lcd.LEFT):
                connectToNXT()
                if b!=None:
                    m_rotate = Motor(b, M_ROTATE)
                    m_rotate.turn(ROTATE_SPEED, 90)
                    if position == "QUARTER": position = "DIME"
                    elif position == "DIME": position = "NICKEL"
                    elif position == "NICKEL": position = "PENNY"
                    elif position == "PENNY": position = "QUARTER"
                    displayCurrentCoinTotal()
                    time.sleep(2)
                    m_rotate.idle() # Allow user fine adjustment
            elif lcd.buttonPressed(lcd.UP):
                if position == "QUARTER": numQuarters += 1
                elif position == "DIME": numDimes += 1
                elif position == "NICKEL": numNickels += 1
                elif position == "PENNY": numPennies += 1
                recalculateTotalAmount()
                displayCurrentCoinTotal()
                time.sleep(.5)
            elif lcd.buttonPressed(lcd.DOWN):
                if position == "QUARTER" and numQuarters!=0: numQuarters -= 1
                elif position == "DIME" and numDimes!=0: numDimes -= 1
                elif position == "NICKEL" and numNickels!=0: numNickels -= 1
                elif position == "PENNY" and numPennies!=0: numPennies -= 1
                recalculateTotalAmount()
                displayCurrentCoinTotal()
                time.sleep(.5)
            
    except KeyboardInterrupt:
        # Say good-bye and save changes to data file before exiting
        displayError("Good-bye!")
        updateDataFile()
        exit()
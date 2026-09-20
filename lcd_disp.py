# functions for 2 line i2c LCD
# Uses circuitpython_i2c_lcd

import board
import busio
from time import sleep, monotonic
from circuitpython_i2c_lcd import I2cLcd

# The PCF8574 has a jumper selectable address: 0x20 - 0x27
lcdAddress = 0x27

# initialise i2c bus
i2c = busio.I2C(board.GP1, board.GP0)

# circuitpython seems to require locking the i2c bus
while i2c.try_lock():
    pass

# initialise the lcd
lcd = I2cLcd(i2c, lcdAddress, 2, 16)

# smiley faces as custom characters
happy = bytearray([0x00,0x0A,0x00,0x04,0x00,0x11,0x0E,0x00])
sad = bytearray([0x00,0x0A,0x00,0x04,0x00,0x0E,0x11,0x00])
grin = bytearray([0x00,0x00,0x0A,0x00,0x1F,0x11,0x0E,0x00])
shock = bytearray([0x0A,0x00,0x04,0x00,0x0E,0x11,0x11,0x0E])
meh = bytearray([0x00,0x0A,0x00,0x04,0x00,0x1F,0x00,0x00])
angry = bytearray([0x11,0x0A,0x11,0x04,0x00,0x0E,0x11,0x00])
tongue = bytearray([0x00,0x0A,0x00,0x04,0x00,0x1F,0x05,0x02])
lcd.custom_char(0, happy)
lcd.custom_char(1, sad)
lcd.custom_char(2, grin)
lcd.custom_char(3, shock)
lcd.custom_char(4, meh)
lcd.custom_char(5, angry)
lcd.custom_char(6, tongue)

def displayText(theText, theRow=0, theIndent=0, theEmoji=-1):
    lcd.move_to(theIndent, theRow)
    lcd.putstr(theText)
    if theEmoji != -1:
        lcd.putchar(" ")
        lcd.putchar(chr(theEmoji))

def displayClear():
    lcd.clear()
    

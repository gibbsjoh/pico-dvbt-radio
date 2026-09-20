import audiopwmio
import audiomp3
import os
import board
from time import sleep
import supervisor
import busio
import digitalio
from stationList import stations
import adafruit_requests
import wifi
import microcontroller
import adafruit_connection_manager
import time
import lcd_disp
import gc

# connect to wifi
print("Connecting...")
wifi.radio.connect(
ssid=os.getenv("CIRCUITPY_WIFI_SSID"),
password=os.getenv("CIRCUITPY_WIFI_PASSWORD")
)
print("Connected! IP address:", wifi.radio.ipv4_address)

# set up connections
netPool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(netPool, ssl_context)

# get the settings from settings.toml
overClock = supervisor.get_setting("overClock")
overClockSettingHz = supervisor.get_setting("overClockSettingHz")

if overClock == 1:
    microcontroller.cpu.frequency = overClockSettingHz
    print("Overclocked to:", microcontroller.cpu.frequency / 1000000, "MHz")
    
def selectStation():
    global stSelected, stCounter, thisStationName, scrollLastTicks, selectLastTicks, debounceMS
    while stSelected == 0:
        oldStationName = thisStationName
        thisStationName = stations[stCounter]
        if oldStationName != thisStationName:
            # update LCD
            lcd_disp.displayText("              ",1,0)
            lcd_disp.displayText(thisStationName,1,0)
        if not scrollButton.value:
            now = supervisor.ticks_ms()
            if now - scrollLastTicks > debounceMS:
                scrollLastTicks = now
                stCounter = stCounter + 1 if stCounter < stTotal else 0
                time.sleep(0.5)
        if not selectButton.value:
            now = supervisor.ticks_ms()
            if now - selectLastTicks > debounceMS:
                selectLastTicks = now
                stSelected = 1
    
def playSelectedStation(stationName):
    global thisAudioOut, selectLastTicks, stCounter, stSelected, transcodeURL, debounceMS, playbackStart, requests, theStream
    thisStationURL = transcodeURL + stationName
    print(thisStationURL)
    try:
        theStream = requests.get(thisStationURL, headers={"connection": "close"}, stream=True)
    except Exception as e:
        print("Failed to open stream:", e)
        while True:
            time.sleep(1)

    decoder = audiomp3.MP3Decoder(theStream.socket)
    print("Starting playback...")

    try:
        thisAudioOut.play(decoder)
        playbackStart = supervisor.ticks_ms()
        lcd_disp.displayClear()
        lcd_disp.displayText("Now Playing")
        lcd_disp.displayText(stationName, 1, 0, 0)
    except Exception as e:
        print("Playback error:", e)

######### Define variables ############
#define buttons for stop, and up/down (tbd)
# define select button - this will also be the stop button!
selectButton = digitalio.DigitalInOut(board.GP20)
selectButton.direction = digitalio.Direction.INPUT
selectButton.pull = digitalio.Pull.UP

#define prev button
scrollButton = digitalio.DigitalInOut(board.GP21)
scrollButton.direction = digitalio.Direction.INPUT
scrollButton.pull = digitalio.Pull.UP

# debounce logic
scrollLastTicks = 0
selectLastTicks = 0
debounceMS = 50

# set up audio out
thisAudioOut = audiopwmio.PWMAudioOut(left_channel=board.GP18, right_channel=board.GP19)
transcodeURL = "http://192.168.0.15:3000/stream?stationName="
# display a "choose station" menu
stTotal = len(stations) - 1
stCounter = 0
stSelected = 0
lcd_disp.displayClear()

refreshDisplay = 1
thisStationName = ""
modeSelect = ""

# select Radio or MP3
while modeSelect == "":
    lcd_disp.displayText("Radio <--> MP3")
    if not selectButton.value:
            now = supervisor.ticks_ms()
            if now - selectLastTicks > debounceMS:
                selectLastTicks = now
                time.sleep(0.5)
                modeSelect = "mp3"
    if not scrollButton.value:
            now = supervisor.ticks_ms()
            if now - scrollLastTicks > debounceMS:
                scrollLastTicks = now
                time.sleep(0.5)
                modeSelect = "radio"

lcd_disp.displayClear()   

if modeSelect == "radio":
    lcd_disp.displayText("Select Station")
    ##### Run the thing! #####
    while True:
        if thisAudioOut.playing is False and stSelected == 0:
            selectStation()
            time.sleep(0.5)
        elif thisAudioOut.playing is False and stSelected == 1:
            playSelectedStation(thisStationName)
        
        ticksNow = supervisor.ticks_ms() # to avoid killing the stream when we select it, wait a few ms before we process the button after playback starts 
        
        if not selectButton.value and thisAudioOut.playing and ticksNow - playbackStart > 1500:
            now = supervisor.ticks_ms()
            if now - selectLastTicks > debounceMS:
                selectLastTicks = now
                thisStationName = ""
                print("Stopping playback.")
                thisAudioOut.stop()
                print("Closing stream.")
                theStream.socket.close()
                lcd_disp.displayClear()
                lcd_disp.displayText("Select Station")
                refreshDisplay = 1
                time.sleep(2)
                stCounter = 0
                stSelected = 0
                gc.collect()
                print("Stopping stream and going back to menu...")
                time.sleep(1)

    
#     global thisStationName
#     global stSelected
#     global scrollButton
#     global debounceMS
#     global stCounter
#     global selectButton
#     global scrollLastTicks
#     global selectLastTicks





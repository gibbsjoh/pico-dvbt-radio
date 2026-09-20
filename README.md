# pico-dvbt-radio
Simple project to play DVB-T radio stations (from TVHeadend) on a Pi Pico.

This is a fairly niche use case - I have a TVHeadend server attached to a DVB-T tuner (UK - so "Freeview") and I wanted a small, possibly battery powered player to stream the available radio stations. There's actually no reason you couldn't also stream audio from TV channels too.

There's 2 parts - a server-side Node.JS program which starts the stream from the TVH box and converts it on the fly to MP3 audio, and the Pi Pico CircuitPython scripts, which present a list of stations and allow you to select which one to play.

Required CircuitPython modules:
adafruit_bus_device
adafruit_character_lcd
adafruit_connection_manager
adafruit_display_text
adafruit_displayio_layout
adafruit_mcp230xx
adafruit_progressbar
adafruit_requests
adafruit_ticks

circuitpython_i2c_lcd



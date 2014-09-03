# Raspberry-Pi-Piggy-Bank-with-Coin-Sorter

The code for a piggy bank and coin sorter I made using a Raspberry Pi, an Arduino, Lego Mindstorms NXT, a coin acceptor, Adafruit's LCD Plate, and a fingerprint sensor. It counts, sorts, and stores coins.

- The Arduino is connected to the Raspberry Pi via a USB hub; it communicates with the fingerprint sensor and detects what kind of coin is inserted.

- A Python script outputs information to the LCD display and stores data in a text file.

Check out the video for this project:
http://youtu.be/XanRVZgY6ow

The code was written by Alex Strandberg and is licensed under the MIT License, check LICENSE for more information

Much of the Arduino code was taken from: http://pastebin.com/z5DnhtSF

A tutorial to set up the Coin Acceptor can be found here:
http://www.instructables.com/id/Make-Money-with-Arduino/?ALLSTEPS

## Arduino Libraries:
- [Adafruit_Fingerprint](https://github.com/adafruit/Adafruit-Fingerprint-Sensor-Library)
- [SoftwareSerial](http://arduino.cc/en/Reference/SoftwareSerial)

## Python Libraries:
- [Adafruit_MCP230xx and Adafruit_CharLCDPlate](https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code)
- [nxt-python](https://code.google.com/p/nxt-python/)
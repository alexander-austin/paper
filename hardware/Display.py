#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


import sys


class Display:


    loggerName = 'display'


    def __init__(self):
        """Initialize."""

        from ..utils import loggingGet
        self.logger = loggingGet(self.loggerName)

        try:

            import RPi.GPIO, spidev
            self.GPIO = RPi.GPIO
            self.SPI = spidev.SpiDev()

        except ImportError:

            self.GPIO = DevGPIO()
            self.SPI = DevSPI()

        #self.logger.error(' '.join([str(sys._getframe().f_code.co_name), 'InterfaceError', repr(e)]))


        return


class DevGPIO:
    IN = 0
    OUT = 0
    BCM = 0
    LOW = 1
    HIGH = 0
    def __init__(self): return
    def output(self, pin, value): return
    def input(self, pin): return 1
    def setmode(self, mode): return
    def setwarnings(self, warnings): return
    def setup(self, pin, direction): return

class DevSPI:
    max_speed_hz = 4000000
    mode = 0b00
    def __init__(self): return
    def writebytes(self, data): return
    def writebytes2(self, data): return
    def open(self, bus, device): return
    def close(self): return
    def cleanup(self, pins): return

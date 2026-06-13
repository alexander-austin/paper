#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


import sys


class GPInput:


    def __init__(self):
        """Initialize."""

        self.state = 'initializing'

        from ..utils import loggingGet, getPaths, jsonLoad
        self.logger = loggingGet(str(self.__class__.__name__).lower())

        self.paths = getPaths()

        self.ioSettings = jsonLoad(self.paths['io_settings'], self.logger)

        if isinstance(self.ioSettings, str):

            self.state = 'error'
            self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'error loading io_settings', self.ioSettings]))
            return

        try:

            import RPi.GPIO, spidev
            self.GPIO = RPi.GPIO
            self.SPI = spidev.SpiDev()

        except ImportError:

            from .DevGPIO import DevGPIO
            self.GPIO = DevGPIO()

            from .DevSPI import DevSPI
            self.SPI = DevSPI()

        #

        if not self.state == 'error': self.state = 'ready'


        return

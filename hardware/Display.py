#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


import time, sys

class Display:


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

        self._startup()

        if not self.state == 'error': self.state = 'ready'


        return


    def displayBufferedBytes(self, bufferedBytes):
        """Displays image from buffered bytes."""

        self._runSequence(
            self.ioSettings[str(self.__class__.__name__).lower()]['sequences']['display'],
            bufferedBytes
        )


        return self.state


    def _startup(self):
        """Begin hardware connection."""

        try:

            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setwarnings(False)

            for pin in self.ioSettings['pins'].keys():

                if self.ioSettings['pins'][pin]['owner'] == str(self.__class__.__name__).lower():

                    if self.ioSettings['pins'][pin]['gpdir'] in ['in', 'out']:

                        self.GPIO.setup(
                            self.ioSettings['pins'][pin]['gpio'],
                            self.GPIO.OUT if self.ioSettings['pins'][pin]['gpdir'] == 'out' else self.GPIO.IN
                        )
                        self.ioSettings['pins'][pin]['active'] = True

                        if self.ioSettings['pins'][pin]['gpdir'] == 'out' and self.ioSettings['pins'][pin]['gpval'] > -1:

                            self.GPIO.output(
                                self.ioSettings['pins'][pin]['gpio'],
                                self.ioSettings['pins'][pin]['gpval']
                            )

            self.SPI.open(
                self.ioSettings[str(self.__class__.__name__).lower()]['spi']['bus'],
                self.ioSettings[str(self.__class__.__name__).lower()]['spi']['device']
            )
            self.SPI.max_speed_hz = self.ioSettings[str(self.__class__.__name__).lower()]['spi']['max_speed_hz']
            self.SPI.mode = bin(
                int(
                    self.ioSettings[str(self.__class__.__name__).lower()]['spi']['mode']['polarity'] * 2
                ) + int(
                    self.ioSettings[str(self.__class__.__name__).lower()]['spi']['mode']['phase']
                )
            )

            self._runSequence(
                self.ioSettings[str(self.__class__.__name__).lower()]['sequences']['init']
            )

        except Exception as e:

            self.state = 'error'
            self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'Exception', repr(e)]))


        return
    def _runSequence(self, sequence, var=None):
        """."""

        if not isinstance(sequence, list):

            self.state = 'error'
            self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'bad sequence format', '']))
            return
        
        for item in sorted(sequence, key=lambda s: s['order']):

            if not self.state == 'error':

                try:

                    if item['type'] == 'var':

                        self.SPI.writebytes(
                            var if isinstance(var, list) else [var]
                        )

                    elif item['type'] == 'var2':

                        self.SPI.writebytes2(
                            var if isinstance(var, list) else [var]
                        )

                    elif item['type'] == 'command':

                        self._runSequence(
                            self.ioSettings[str(self.__class__.__name__).lower()]['sequences']['command'],
                            hex(item['data'])
                        )

                    elif item['type'] == 'data':

                        self._runSequence(
                            self.ioSettings[str(self.__class__.__name__).lower()]['sequences']['data'],
                            hex(item['data'])
                        )

                    elif item['type'] == 'data2':

                        self._runSequence(
                            self.ioSettings[str(self.__class__.__name__).lower()]['sequences']['data2'],
                            item['data']
                        )

                    elif item['type'] == 'sequence':

                        self._runSequence(
                            self.ioSettings[str(self.__class__.__name__).lower()]['sequences'][item['data']]
                        )

                    elif item['type'] == 'sleep':

                        time.sleep(item['data'] / 1000.0)

                    elif item['type'] == 'read':

                        if not self._readWait() == True:

                            self.state = 'error'
                            self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'Read wait timeout', '']))

                    elif item['type'].startswith('pin_'):

                        self.GPIO.output(
                            self._getNamedPinValue(item['type'][4:], 'gpio'),
                            item['data']
                        )

                except Exception as e:

                    self.state = 'error'
                    self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'Exception', repr(e)]))
                    break


        return
    def _readWait(self):
        """Polls busy state. Ready = True. Timeout/error = False."""

        tries = 0

        while tries < self.ioSettings[str(self.__class__.__name__).lower()]['busy_polls']:

            try:

                if not self.GPIO.input(self._getNamedPinValue('busy', 'gpio')) == 0:

                    return True

            except Exception as e:

                self.state = 'error'
                self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'Exception', repr(e)]))
                break

            tries += 1
            time.sleep(self.ioSettings[str(self.__class__.__name__).lower()]['busy_wait'] / 1000.0)


        return False
    def _getNamedPinValue(self, name, key):
        """Get pin value based on name."""

        for pin in self.ioSettings['pins'].keys():

            if self.ioSettings['pins'][pin]['owner'] == str(self.__class__.__name__).lower():

                if self.ioSettings['pins'][pin]['name'] == name:

                    return self.ioSettings['pins'][pin][key]


        return

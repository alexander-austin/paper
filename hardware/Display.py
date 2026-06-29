#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


import os, sys, time
from HardwareBase import HardwareBase
from utils import Imager

class Display(HardwareBase):


    def __init__(self, *args, **kwargs):
        """Initialize."""
        super(Display, self).__init__(*args, **kwargs)

        self.orientation = 'landscape'
        self.imager = Imager()
        self.imager.setDisplayOrientation(self.orientation)

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


        if not self.state['value']['state'] == 'error': self._setState('ready')


        return

    def run(self):
        """Main loop."""

        while True:

            events = self._getEvents()

            for event in events:

                if event['value']['intent'] == 'orientation':

                    if not self.orientation == event['value']['orientation']['orientation']:

                        self.orientation = event['value']['orientation']['orientation']

                        if 'file' in event['value'].keys():

                            self.currentFilePath = os.path.join(self.paths['media']['path'], event['value']['file'])

                        self.displayOrientationChange()

                elif event['value']['intent'] in ['next', 'back', 'show']:

                    if 'file' in event['value'].keys():

                        self.displayFileName(event['value']['file'])

            time.sleep(self.ioSettings[str(self.__class__.__name__).lower()]['run_interval'])


    def displayFileName(self, fileName):
        """Displays image from file name."""

        self._displayFilePath(os.path.join(self.paths['media']['path'], fileName))


        return
    def displayOrientationChange(self):
        """Displays image from file name."""

        if hasattr(self, 'currentFilePath'):

            self._displayFilePath(self.currentFilePath)


        return

    def _displayFilePath(self, filePath):
        """Displays image from file path."""

        if os.path.exists(filePath):

            try:

                self.imager.setDisplayOrientation(self.orientation)
                quantizedBuffer = self.imager.getQuantizedBuffer(filePath)

                self._displayBufferedBytes(quantizedBuffer)

                self.currentFilePath = filePath

            except Exception as e:

                self._setState('error', error=' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), repr(e)]))


        return
    def _displayBufferedBytes(self, bufferedBytes):
        """Displays image from buffered bytes."""

        if isinstance(bufferedBytes, list):

            if len(bufferedBytes) > 0:

                self._runSequence(
                    self.ioSettings[str(self.__class__.__name__).lower()]['sequences']['display'],
                    bufferedBytes
                )


        return

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

            self._setState('error', error=' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), repr(e)]))



        return
    def _runSequence(self, sequence, var=None, isChild=False):
        """Run sequence of I/O operations."""

        if self.state['value']['state'] == 'error': return

        self._setState('working')

        if not isinstance(sequence, list):

            self._setState('error', error=' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'bad sequence format', '']))
            return
        
        for item in sorted(sequence, key=lambda s: s['order']):

            if not self.state['value']['state'] == 'error':

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
                            var=hex(item['data']),
                            isChild=True
                        )

                    elif item['type'] == 'data':

                        self._runSequence(
                            self.ioSettings[str(self.__class__.__name__).lower()]['sequences']['data'],
                            var=hex(item['data']),
                            isChild=True
                        )

                    elif item['type'] == 'data2':

                        self._runSequence(
                            self.ioSettings[str(self.__class__.__name__).lower()]['sequences']['data2'],
                            var=item['data'],
                            isChild=True
                        )

                    elif item['type'] == 'sequence':

                        self._runSequence(
                            self.ioSettings[str(self.__class__.__name__).lower()]['sequences'][item['data']],
                            isChild=True
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

                    self._setState('error', error=' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'Exception', repr(e)]))
                    break

        if isChild == False:

            if not self.state['value']['state'] == 'error': self._setState('ready')


        return
    def _readWait(self):
        """Polls busy state. Ready = True. Timeout/error = False."""

        if self.state['value']['state'] == 'error': return False
        self._setState('waiting')

        tries = 0

        while tries < self.ioSettings[str(self.__class__.__name__).lower()]['busy_polls']:

            try:

                if not self.GPIO.input(self._getNamedPinValue('busy', 'gpio')) < 0.5:

                    self.state = 'ready'
                    return True

            except Exception as e:

                self._setState('error', error=' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'Exception', repr(e)]))
                break

            tries += 1
            time.sleep(self.ioSettings[str(self.__class__.__name__).lower()]['busy_wait'] / 1000.0)

        if not self.state['value']['state'] == 'error': self._setState('ready')


        return False
    def _getNamedPinValue(self, name, key):
        """Get pin value based on name."""

        for pin in self.ioSettings['pins'].keys():

            if self.ioSettings['pins'][pin]['owner'] == str(self.__class__.__name__).lower():

                if self.ioSettings['pins'][pin]['name'] == name:

                    return self.ioSettings['pins'][pin][key]


        return
    def _getEventMethodAndArgs(self):
        """."""


        return None, None

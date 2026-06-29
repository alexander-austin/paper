#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


import sys, time
from utils import timestampEpoch
from HardwareBase import HardwareBase


class GPInput(HardwareBase):


    def __init__(self, *args, **kwargs):
        """Initialize."""
        super(HardwareBase, self).__init__(*args, **kwargs)

        self.source = '%(component_key)s_%(gpio)s' % {
            'component_key': str(self.__class__.__name__).lower(),
            'gpio': str('00%d' % (pin['gpio'], ))[-2:]
        }

        if not isinstance(self.gpio, int):

            self._setState('error', error=' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'invalid gpio']))
            return

        if self.gpio == -1:

            self._setState('error', error=' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'invalid gpio']))
            return

        self.history = {
            'poll': 0.0,
            'trigger': 0.0,
            'values': []
        }

        try:

            import RPi.GPIO, spidev
            self.GPIO = RPi.GPIO
            self.SPI = spidev.SpiDev()

        except ImportError:

            from .DevGPIO import DevGPIO
            self.GPIO = DevGPIO()

            from .DevSPI import DevSPI
            self.SPI = DevSPI()

        try:

            for pin in self.ioSettings['pins'].keys():

                if self.ioSettings['pins'][pin]['owner'] == str(self.__class__.__name__).lower() and self.ioSettings['pins'][pin]['gpio'] == self.gpio and self.ioSettings['pins'][pin]['gpdir'] == 'in':

                    self.GPIO.setmode(self.GPIO.BCM)
                    self.GPIO.setwarnings(False)

                    self.GPIO.setup(
                        self.gpio,
                        self.GPIO.IN
                    )

        except Exception as e:

            self._setState('error', error=' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), repr(e)]))

        if not self.state['value']['state'] == 'error': self._setState('ready')


        return


    def run(self):
        """Main loop."""

        while True:

            self.poll()

            time.sleep(self.ioSettings[str(self.__class__.__name__).lower()]['run_interval'])


    def poll(self):
        """Poll gpio value."""

        # Poll raw value
        inputValue = self.GPIO.input(self.gpio)

        pollValue = {
            'timestamp': timestampEpoch(),
            'type': 'up' if inputValue < 0.5 else 'down'
        }

        latestValue = self._latestValue()

        if isinstance(latestValue, dict):

            if not latestValue['type'] == pollValue['type']:

                self.history['values'].append(pollValue)

        else:

            self.history['values'].append(pollValue)

        self._handleEvent()

        self.history['poll'] = timestampEpoch()


        return


    def _latestValue(self):
        """Get most current poll value."""

        if len(self.history['values']) > 0:

            latestTimestamp = 0.0

            for value in self.history['values']:

                if value['timestamp'] > latestTimestamp:

                    latestTimestamp = value['timestamp']

            for value in self.history['values']:

                if value['timestamp'] == latestTimestamp:

                    return value


        return
    def _handleEvent(self):
        """Check for events and handle."""

        def shouldRetain(valueTimestamp, currentTimestamp):

            if valueTimestamp > (currentTimestamp - self.ioSettings[str(self.__class__.__name__).lower()]['durations']['history']):

                return True


            return False
        def shouldTrigger(eventTimestamp):

            if eventTimestamp >= (self.history['trigger'] + self.ioSettings[str(self.__class__.__name__).lower()]['durations']['gap']):

                if self.history['poll'] == 0.0 or (eventTimestamp >= (self.history['poll'] - self.ioSettings[str(self.__class__.__name__).lower()]['durations']['gap']) and eventTimestamp < ((self.history['poll'] - self.ioSettings[str(self.__class__.__name__).lower()]['durations']['gap']) + self.ioSettings[str(self.__class__.__name__).lower()]['durations']['poll'])):

                    return True


            return False
        def withinGap(timestamp1, timestamp2):

            duration = abs(timestamp1 - timestamp2)

            if duration <= self.ioSettings[str(self.__class__.__name__).lower()]['durations']['gap']:

                return True


            return False
        def isShort(value1, value2):

            duration = abs(value1['timestamp'] - value2['timestamp'])

            if duration >= self.ioSettings[str(self.__class__.__name__).lower()]['durations']['short']['min'] and duration < self.ioSettings[str(self.__class__.__name__).lower()]['durations']['short']['max']:

                return True


            return False
        def isLong(value1, value2):

            duration = abs(value1['timestamp'] - value2['timestamp'])

            if duration >= self.ioSettings[str(self.__class__.__name__).lower()]['durations']['long']['min'] and duration < self.ioSettings[str(self.__class__.__name__).lower()]['durations']['long']['max']:

                return True


            return False

        currentTimestamp = timestampEpoch()

        sortedValues = sorted(self.history['values'], key=lambda v: v['timestamp'], reverse=True)

        if len(sortedValues) > 0:

            triggered = False
            retainedValues = []

            for v in range(len(sortedValues)):

                if shouldRetain(sortedValues[v]['timestamp'], currentTimestamp):

                    if sortedValues[v]['type'] == 'up':

                        if len(sortedValues) > (v + 1):

                            if sortedValues[v + 1]['type'] == 'down':

                                if triggered == False and shouldTrigger(max(sortedValues[v]['timestamp'], sortedValues[v + 1]['timestamp'])):

                                    if isShort(sortedValues[v], sortedValues[v + 1]) == True:

                                        # Double short click
                                        if len(sortedValues) > (v + 3) and self.ioSettings[str(self.__class__.__name__).lower()]['double'] == True:

                                            if sortedValues[v + 2]['type'] == 'up' and sortedValues[v + 3]['type'] == 'down':

                                                if isShort(sortedValues[v + 2], sortedValues[v + 3]) == True:

                                                    if withinGap(min(sortedValues[v]['timestamp'], sortedValues[v + 1]['timestamp']), max(sortedValues[v + 2]['timestamp'], sortedValues[v + 3]['timestamp'])):

                                                        self._addEvent({'event': 'short_double'})
                                                        triggered = True
                                                        self.history['trigger'] = timestampEpoch()

                                        if triggered == False:

                                            self._addEvent({'event': 'short'})
                                            triggered = True
                                            self.history['trigger'] = timestampEpoch()

                                    elif isLong(sortedValues[v], sortedValues[v + 1]) == True:

                                        # Double long click
                                        if len(sortedValues) > (v + 3) and self.ioSettings[str(self.__class__.__name__).lower()]['double'] == True:

                                            if sortedValues[v + 2]['type'] == 'up' and sortedValues[v + 3]['type'] == 'down':

                                                if isLong(sortedValues[v + 2], sortedValues[v + 3]) == True:

                                                    if withinGap(min(sortedValues[v]['timestamp'], sortedValues[v + 1]['timestamp']), max(sortedValues[v + 2]['timestamp'], sortedValues[v + 3]['timestamp'])):

                                                        self._addEvent({'event': 'long_double'})
                                                        triggered = True
                                                        self.history['trigger'] = timestampEpoch()

                                        if triggered == False:

                                            self._addEvent({'event': 'long'})
                                            triggered = True
                                            self.history['trigger'] = timestampEpoch()

                    retainedValues.append(sortedValues[v])

            # Repopulate value history
            self.history['values'] = []
            for retainedValue in retainedValues: self.history['values'].append(retainedValue)


        return

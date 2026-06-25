#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


import math, time
from HardwareBase import HardwareBase


class Mpu6050(HardwareBase):


    def __init__(self):
        """Initialize."""
        super(Mpu6050, self).__init__()

        self.values = {}

        try:

            from smbus2 import SMBus
            self.bus = SMBus(self.ioSettings[str(self.__class__.__name__).lower()]['bus'])

        except ImportError:

            from .DevSMBus import DevSMBus
            self.bus = DevSMBus(self.ioSettings[str(self.__class__.__name__).lower()]['bus'])

        self.write(
            self.registers['rate_sample'],
            7
        )
        self.write(
            self.ioSettings[str(self.__class__.__name__).lower()]['registers']['power_management'],
            1
        )
        self.write(
            self.ioSettings[str(self.__class__.__name__).lower()]['registers']['config'],
            1
        )
        self.write(
            self.ioSettings[str(self.__class__.__name__).lower()]['registers']['gyro']['config'],
            24
        )
        self.write(
            self.ioSettings[str(self.__class__.__name__).lower()]['registers']['interrupt_state'],
            1
        )

        if not self.state['value']['state'] == 'error': self._setState('ready')

        self.run()


        return


    def run(self):
        """Main loop."""

        while True:

            self.poll()

            time.sleep(self.ioSettings[str(self.__class__.__name__).lower()]['run_interval'])


    def poll(self):
        """Poll (smoothed) values for accelerometer & gyro, then infer orientation."""

        values = {}

        if not self.state['value']['state'] == 'error':

            self.errorCount = 0

            for meterKey in ['accelerometer', 'gyro']:

                values[meterKey] = dict(
                    [
                        (
                            d,
                            sum(
                                [
                                    self._read(
                                        self.ioSettings[str(self.__class__.__name__).lower()]['registers'][meterKey][d]
                                    ) / self.ioSettings[str(self.__class__.__name__).lower()]['registers'][meterKey]['denominator']
                                    for v in range(self.ioSettings[str(self.__class__.__name__).lower()]['smoothing'])
                                ]
                            ) / self.ioSettings[str(self.__class__.__name__).lower()]['smoothing']
                        )
                        for d in ['x', 'y', 'z']
                    ]
                )

            values['orientation'] = {
                'pitch': 180.0 * math.atan(values['accelerometer']['x'] / math.sqrt(math.pow(values['accelerometer']['y'], 2) + math.pow(values['accelerometer']['z'], 2))) / math.pi,
                'roll': 180.0 * math.atan(values['accelerometer']['y'] / math.sqrt(math.pow(values['accelerometer']['x'], 2) + math.pow(values['accelerometer']['z'], 2))) / math.pi,
                'yaw': 180.0 * math.atan(values['accelerometer']['z'] / math.sqrt(math.pow(values['accelerometer']['x'], 2) + math.pow(values['accelerometer']['z'], 2))) / math.pi
            }

            if (values['orientation']['roll'] >= -45.0 and values['orientation']['roll'] <= 45.0) or (values['orientation']['roll'] >= 135.0 and values['orientation']['roll'] <= 225.0):

                values['orientation']['orientation'] = 'landscape'

            else:

                values['orientation']['orientation'] = 'portrait'

        values['state'] = self.state['value']['state']
        values['error_count'] = self.errorCount

        # Trigger event
        if not values['orientation']['orientation'] == self.values['orientation']['orientation']:

            self._addEvent({'event': 'orientation', 'value': values['orientation']['orientation']})

        self.values = values


        return


    def _read(self, register):
        """Reads raw data from device bus."""

        value = 0

        if not self.state['value']['state'] == 'error':

            try:

                hi = self.bus.read_byte_data(
                    hex(self.ioSettings[str(self.__class__.__name__).lower()]['address']),
                    hex(register)
                )
                lo = self.bus.read_byte_data(
                    hex(self.ioSettings[str(self.__class__.__name__).lower()]['address']),
                    hex(register + 1)
                )

                value = ((hi << 8) | lo) if ((hi << 8) | lo) <= 32768 else (((hi << 8) | lo) - 65536)

            except: self.errorCount += 1


        return value
    def _write(self, register, value):
        """Writes to device bus."""

        try:

            self.bus.write_byte_data(
                hex(self.ioSettings[str(self.__class__.__name__).lower()]['address']),
                hex(register),
                value
            )

        except: self._setState('error', error='write')


        return

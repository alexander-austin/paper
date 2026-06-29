#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


import multiprocessing, time, sys
from HardwareBase import HardwareBase
from Display import Display
from GPInput import GPInput
from Mpu6050 import Mpu6050


class HardwareManager(HardwareBase):


    def __init__(self):
        """Initialize."""
        super(HardwareBase, self).__init__()

        self._startup()

        if not self.state['value']['state'] == 'error': self._setState('ready', sendToApi=False)

        self.run()


        return


    def run(self):
        """Main loop."""

        while True:

            try:

                for p in range(len(self.processes)):

                    if self.processes[p]['process'] is None or not self.processes[p]['process'].is_alive():

                        if not self.processes[p]['class'] is None:

                            self.processes[p]['instance'] = self.processes[p]['class'](
                                self.processes[p]['args'],
                                self.processes[p]['kwargs']
                            )

                            self.processes[p]['process'] = multiprocessing.Process(
                                target=self.processes[p]['instance'].run
                            )

                            self.processes[p]['process'].start()
                            self.processes[p]['process'].join()

            except Exception as e:

                self._setState('error', error=' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), repr(e)]), sendToApi=False)

            time.sleep(5.0)


    def _startup(self):
        """Initial configuration."""

        self.processes = []

        try:

            for componentKey in self.ioSettings.keys():

                if 'run_interval' in self.ioSettings[componentKey].keys():

                    if self.ioSettings[componentKey]['pin_owner'] == True:

                        for pin in self.ioSettings['pins']:

                            if pin['owner'] == componentKey and pin['active'] == True:

                                self.processes.append(
                                    {
                                        'name': '%(component_key)s_%(gpio)s' % {
                                            'component_key': componentKey,
                                            'gpio': str('00%d' % (pin['gpio'], ))[-2:]
                                        },
                                        'class': Display if componentKey == 'display' else (
                                            Mpu6050 if componentKey == 'mpu6050' else (
                                                GPInput if componentKey == 'gpinput' else None
                                            )
                                        ),
                                        'instance': None,
                                        'args': tuple(),
                                        'kwargs': {
                                            'gpio': pin['gpio']
                                        },
                                        'process': None
                                    }
                                )

                    else:

                        self.processes.append(
                            {
                                'name': componentKey,
                                'class': Display if componentKey == 'display' else (
                                    Mpu6050 if componentKey == 'mpu6050' else (
                                        GPInput if componentKey == 'gpinput' else None
                                    )
                                ),
                                'instance': None,
                                'args': tuple(),
                                'kwargs': {},
                                'process': None
                            }
                        )

        except Exception as e:

            self._setState('error', error=' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), repr(e)]), sendToApi=False)


        return


if __name__ == '__main__':

    hardwareManager = HardwareManager()

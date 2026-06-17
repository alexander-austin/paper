#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


class DevSMBus(object):
    def __init__(self, bus=None, force=False): return
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.close()
    def open(self, bus): return
    def close(self): return
    def _get_pec(self): return self._pec
    def enable_pec(self, enable=True): return
    pec = property(_get_pec, enable_pec)
    def _set_address(self, address, force=None): return
    def _get_funcs(self): return
    def write_quick(self, i2c_addr, force=None): return
    def read_byte(self, i2c_addr, force=None): return
    def write_byte(self, i2c_addr, value, force=None): return
    def read_byte_data(self, i2c_addr, register, force=None): return
    def write_byte_data(self, i2c_addr, register, value, force=None): return
    def read_word_data(self, i2c_addr, register, force=None): return
    def write_word_data(self, i2c_addr, register, value, force=None): return
    def process_call(self, i2c_addr, register, value, force=None): return
    def read_block_data(self, i2c_addr, register, force=None): return
    def write_block_data(self, i2c_addr, register, data, force=None): return
    def block_process_call(self, i2c_addr, register, data, force=None): return

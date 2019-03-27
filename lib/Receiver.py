import os
import zlib
import time
from fsm import Receiver

class Receiver_Driver:

    def __init__(self, state_mach, file_name=os.path.join('..', 'files', 'out.txt'), serialPort=None):
        self.__packet_list = []

        self.__my_fsm = state_mach
        self.__serialPort = serialPort

        self.__file_name = file_name
        self.__file = open(self.__file_name, "w")
        self.__file.write('')
        self.__file.close()
        self.__file = open(self.__file_name, "ab")

        self.__packets_to_receive = 0
        self.__zero_padding = 0

        self.__flag = 0

    @property
    def packet_list(self):
        return self.__packet_list

    @packet_list.setter
    def packet_list(self, data):
        return self.__packet_list.append(data)

    @property
    def my_fsm(self):
        return self.__my_fsm

    @property
    def serialPort(self):
        return self.__serialPort

    @serialPort.setter
    def serialPort(self, port):
        self.__serialPort = port

    @property
    def file_name(self):
        return self.__file_name

    @file_name.setter
    def file_name(self, fn):
        self.__file_name = fn

    @property
    def file(self):
        return self.__file

    @property
    def packets_to_receive(self):
        return self.__packets_to_receive

    @packets_to_receive.setter
    def packets_to_receive(self, num):
        self.__packets_to_receive = num

    @property
    def zero_padding(self):
        return self.__zero_padding

    @zero_padding.setter
    def zero_padding(self, pad):
        self.__zero_padding = pad

    @property
    def flag(self):
        return self.__flag

    @flag.setter
    def flag(self, data):
        self.__flag = data

    def parse_meta(self):
        self.flag = 0
        packet_obj = self.serialPort.read(64)
        packet_num = int.from_bytes(packet_obj[:4], 'big')
        checksum = int.from_bytes(packet_obj[60:], 'big')
        data = packet_obj[4:60]
        crc = zlib.crc32(data) & 0xffffffff
        if (crc == checksum or crc == checksum + 1 or crc == checksum - 1) and packet_num == 0:
            self.packets_to_receive = int.from_bytes(data[0:4], 'big')
            self.zero_padding = int.from_bytes(data[4:5], 'big')
            file_ext = []
            for bit in packet_obj[5:]:
                if bit != b'0':
                    file_ext.append(bit)
                else:
                    pass
            time.sleep(.025)
            self.my_fsm.on_event("")
            self.data_loop()
        else:
            print(packet_obj)
            self.flag = 1
            self.my_fsm.state = Receiver()

    def data_checker(self, data, checksum):
        calc_crc = zlib.crc32(data)
        if (checksum == calc_crc):
            self.packet_list = data
            self.file.write(data)
        else:
            self.packet_list = "ERROR"
            
    def data_loop(self):
        packet_obj = self.serialPort.read(64)

        while packet_obj != b'':
            packet_num = int.from_bytes(packet_obj[:4], 'big')
            checksum = int.from_bytes(packet_obj[60:], 'big')
            payload = packet_obj[4:60]
            self.data_checker(payload, checksum)
            packet_obj = self.serialPort.read(64)

        i = 0
        errors = 0
        while i < len(self.packet_list):
            if self.packet_list[i] == "ERROR":
                errors += 1
            else:
                i += 1
        if errors > 0:
            self.resend_packet()
            self.my_fsm.on_event("resend")
        else:
            self.finish_packet()
            self.my_fsm.on_event("finish")

        self.file.close()

    def finish_packet(self):
        index = "DONE"
        index = bytes(index.encode('utf-8'))
        payload = "THIS FILE HAS BEEN RECEIVED WITH NO ERRORS"
        payload = bytes(payload.encode('utf-8'))
        padding = b'0' * 14
        done = payload + padding
        done_crc = zlib.crc32(done) & 0xffffffff
        done_crc = done_crc.to_bytes(4, 'big')
        done = index + payload + padding + done_crc
        self.flag = 1
        self.serialPort.write(done)

    def resend_packet(self):
        index = "RESE"
        index = bytes(index.encode('utf-8'))
        error_idx = [i for i, e in enumerate(self.packet_list) if e == "ERROR"]
        idx_to_send = []
        for idx in error_idx:
            idx_to_send.append(idx.to_bytes(4, 'big'))
        padding_size = (14 - len(idx_to_send)) * 4
        padding = b'0' * padding_size
        resend = index + idx_to_send[:-1] + padding
        self.serialPort.write(resend)

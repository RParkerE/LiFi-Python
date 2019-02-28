import math
import zlib
import time
import os


class Sender_Driver:
#def sender_driver(file_name, serialPort):

    def __init__(self, file_name, serialPort):
        self.__packet_list = []

        self.__serialPort = serialPort

        self.__file = open(file_name, 'rb')
        self.__file_obj = self.__file.read()
        self.__file_size = len(self.__file_obj)
        self.__packet_num = math.ceil(self.__file_size/56)
        self.__padding_size = 56 - (self.__file_size % 56)
        self.__padding = '0' * self.__padding_size
        self.__file_obj = self.__file_obj + self.__padding.encode('utf-8')
        self.__file_data = list(zip(*[iter(self.__file_obj)]*56))

    @property
    def packet_list(self):
        return self.__packet_list

    @packet_list.setter
    def packet_list(self, data):
        return self.__packet_list.append(data)

    @property
    def serialPort(self):
        return self.__serialPort

    @property
    def file(self):
        return self.__file.name

    @property
    def packet_num(self):
        return self.__packet_num

    @property
    def padding_size(self):
        return self.__padding_size

    @property
    def file_data(self):
        return self.__file_data
    
    

    def meta_creator(self):
        index = 0
        file_name = self.file
        index = index.to_bytes(4, 'big')
        param_1 = self.packet_num.to_bytes(4, 'big')
        param_2 = self.padding_size.to_bytes(1, 'big')
        # TODO: Better implementation of this
        junk, file_extension = os.path.splitext(file_name)
        param_3 = bytes(file_extension.encode('utf-8'))
        padding = b'0' * 51
        meta = index + param_1 + param_2 + param_3 + padding
        meta_crc = zlib.crc32(meta) & 0xffffffff
        meta_crc = meta_crc.to_bytes(4, 'big')
        meta = index + param_1 + param_2 + param_3 + padding + meta_crc
        return meta
        
        

    # Packet Creator adding 4 bytes index to 48 bytes of data
    def packet_creator(self, counter):
        data = self.file_data[0][counter]
        data_byte = bytes(data)
        counter += 1
        index = counter.to_bytes(4, 'big')
        data_crc = zlib.crc32(data_byte) & 0xffffffff
        data_crc = data_crc.to_bytes(4, 'big')
        packet = index + data_byte + data_crc
        self.packet_list = packet
        return packet


    def packet_loop(self):
        i = 0
        while i < self.packet_num:
            out_packet = self.packet_creator(i)
            #self.serialPort.write(out_packet)
            time.sleep(0.1)
            i += 1
            return out_packet

        self.file.close()
        
        

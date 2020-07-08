#!/usr/bin/env python3

import can

# The following is a utility class with functions to help read data from a hex file
# It relies on reading from a hex file and keeps track of the current position

#TODO
# verify function inputs are valid
# verify hex file is valid by calculating all checksums in the file, and eof and addresses, etc


# Hex file details

# Entries in hex files follow this format
#
# :llaaaatt[dd...dd]cc
#
# :          signifies the start of a line
# ll         signifies the number of bytes in the data record
# aaaa       signifies the address of this data field
# tt         signifies the record type
# [dd...dd]  signifies the data bytes
# cc         signifies the two byte checksum

# hex data fields
RECORD_LENGTH_FIELD = slice(1,3)
ADDRESS_FIELD = slice(3,7)
TYPE_FIELD = slice(7,9)
# DATA_FIELD depends on record length
# CHECKSUM_FIELD depends on data length

# hex record types
DATA = "00"
EXTENDED = "04"

class HexUtility:
    def __init__(self):
        self.curr_line_index = 0 # current line in hex file
        self.first_8 = True      # reading the first 8 or second 8 bytes
        self.is_eof = False

    # open a hex file and store all the lines into a string
    def open_file(self, hex_file_path): 
        self.hex_file_path = hex_file_path
        self.hex_file = open(self.hex_file_path, "r")
        self.hex_lines = self.hex_file.readlines()
    
    # the following five functions extract a certain field given an entry
    def get_record_length(self, line):
        return line[RECORD_LENGTH_FIELD]

    def get_address(self, line):
        return line[ADDRESS_FIELD]
    
    def get_type(self, line):
        return line[TYPE_FIELD]

    def get_data_bytes(self, line, start=0, num_bytes=-1): # start is an index relative to the first byte, so 8 means start from the 8th bytes
        # need to check if num bytes is valid, throw exception if not
        start = start*2
        if num_bytes == -1:  # then get all bytes
            return line[9+start:9+start + 2*int(self.get_record_length(line))] # record length in bytes, two hex chars are a byte
        return line[9+start:9+start + 2*num_bytes]

    def get_checksum(self, line):
        return line[9 + 2*int(self.get_record_length(line)):9 + 2*int(self.get_record_length(line)) + 2] # don't know if have newline or not, safer to start from begginging
    
    # gets the start address by parsing the first and/or second line
    def get_start_address(self): # returns it as a string
        first_line = self.hex_lines[0]
        if self.get_type(first_line) == "04": # if extended address
            top_16_bits = self.get_data_bytes(first_line) # stored in data bytes
            second_line = self.hex_lines[1]
            if self.get_type(second_line) == "00": # if the first data line
                bottom_16_bits = self.get_address(second_line)
                start_address = top_16_bits + bottom_16_bits
                return start_address
        return self.get_address(first_line)

    # calculates the checksum of an entry in the hex file
    def calc_checksum(self, line):
        bytes_list = [line[i:i+2] for i in range(0, len(line), 2)]
        bytes_list_num = [int(i, 16) for i in bytes_list]
        two_compl = (256 - sum(bytes_list_num)) % 256
        return (hex(two_compl)[2:]).zfill(2)

    # used to get the next data bytes in the hex file based on the current "read state", returns -1 if eof
    def get_next_data_8(self): # gets the next 8 bytes, keeps track using self.curr_line
        # find next data line
        data_bytes = ""
        if self.get_type(self.hex_lines[self.curr_line_index]) == "01" or self.get_type(self.hex_lines[self.curr_line_index]) == "05":
            self.is_eof = True
            return -1
        
        while self.get_type(self.hex_lines[self.curr_line_index]) != "00":
            self.curr_line_index +=1
        if self.first_8:
            self.first_8 = False 
            data_bytes = self.get_data_bytes(self.hex_lines[self.curr_line_index], 0, 8)
        else:
            self.first_8 = True
            data_bytes = self.get_data_bytes(self.hex_lines[self.curr_line_index], 8, 8) 
            self.curr_line_index +=1
        
        bytes_list = [data_bytes[i:i+2] for i in range(0, len(data_bytes), 2)]
        bytes_list_num = [int(i, 16) for i in bytes_list]
        return bytes_list_num

    def __del__(self):
        print("closing file")
        self.hex_file.close()

# helper function independent of class
def make_socketcan_packet(can_id, data_bytes): # pass in data as a list of 8 bytes
        return can.Message(arbitration_id=can_id, data=[data_bytes[0], data_bytes[1], data_bytes[2],
                                                        data_bytes[3], data_bytes[4], data_bytes[5], 
                                                        data_bytes[6], data_bytes[7]], is_extended_id=False)
        

# for the actual can class make it easy to send messages, abstract away socket can
# for example can say "send data size __" or "send start address __" functions

# also make a translate function that translates socketcan messages

#also make function to read and translate hex file

# also make function to check timeout
# hexUtil = HexUtility()
# hexUtil.open_file("2.27_copy.hex")
# print(make_socketcan_packet(0x04F,hexUtil.get_next_data_8()))
# print(make_socketcan_packet(0x050,hexUtil.get_next_data_8()))
# print(make_socketcan_packet(0x051,hexUtil.get_next_data_8()))
# print(make_socketcan_packet(0x052,hexUtil.get_next_data_8()))
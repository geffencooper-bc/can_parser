import argparse
from decoder import *
import sys
sys.path.insert(1, '/home/geffen.cooper/Desktop/kinetek_scripts/ota_scripts/')
from HexUtility import *

if __name__ == "__main__":
    #----------------------csv test----------------
    # kin_csv = Decoder("csv")
   
    # # pass in the file to parse as a command line arg
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--csv_file", required=True)
    # args = parser.parse_args()
    # file_name = args.csv_file

    # with open(file_name, 'r') as csv_file:
    #     reader = csv.reader(csv_file)
    #     for row in reader:
    #         response = kin_csv.decode_frame(row)
    #         if response != None:
    #             pass
    #             print(response)
    #     print(kin_csv.hex_data)




    # #----------------------socket_can test--------------------
    # note calling the decode function multiple times may cause duplication
    # of the recreated hex data. Store return value in a variable as shown.

    # this is a hard coded test, need a more flexible script that just reads from the hex file

    def decode_socket(frame): # only accounts for id a data
        can_id = hex(frame.arbitration_id)[2:].zfill(3)
        data = ""
        for byte in frame.data:
           data += hex(byte)[2:].zfill(2).upper() + " "
        return str(can_id + " | " + data[:-1])

    # make a kinetek socketcan decoder
    kin_socketcan = Decoder("socketcan")

    # send enter IAP mode command
    msg = can.Message(arbitration_id=0x048, data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
    print("SENT:\t", msg)
    resp = kin_socketcan.decode_frame(msg)
    print("RECEIVED:\t", resp)
    while decode_socket(resp) != "060 | 08 00 00 00 00":
        resp = kin_socketcan.decode_frame(msg)
        print("RECEIVED:\t", resp)

    print("entered IAP mode")
    
    # ask kinetek if can start sending data bytes
    msg = can.Message(arbitration_id=0x048, data=[0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88], is_extended_id=False)
    print("SENT:\t", msg)
    resp = kin_socketcan.decode_frame(msg)
    print("RECEIVED:\t", resp)
    while decode_socket(resp) != "069 | 99 99 99 99 99 99 99 99":
        resp = kin_socketcan.decode_frame(msg)
        print("RECEIVED:\t", resp)

    print("can start sending bytes")

    msg = can.Message(arbitration_id=0x048, data=[0x02, 0x08, 0x00, 0x80, 0x00, 0x9A, 0x00, 0x00], is_extended_id=False)
    print("SENT:\t", msg)
    resp = kin_socketcan.decode_frame(msg)
    print("RECEIVED:\t", resp)
    while decode_socket(resp) != "069 | 02 10 10 10 10 10 10 10":
        resp = kin_socketcan.decode_frame(msg)
        print("RECEIVED:\t", resp)
    
    print("start address received")

    msg = can.Message(arbitration_id=0x048, data=[0x03, 0x00, 0x87, 0x47, 0xFE, 0x9B, 0x00, 0x00], is_extended_id=False)
    print("SENT:\t", msg)
    resp = kin_socketcan.decode_frame(msg)
    print("RECEIVED:\t", resp)
    while decode_socket(resp) != "069 | 03 10 10 10 10 10 10 10":
        resp = kin_socketcan.decode_frame(msg)
        print("RECEIVED:\t", resp)

    print("checksum data received")

    msg = can.Message(arbitration_id=0x048, data=[0x04, 0x00, 0x01, 0x68, 0x30, 0x9C, 0x00, 0x00], is_extended_id=False)
    print("SENT:\t", msg)
    resp = kin_socketcan.decode_frame(msg)
    print("RECEIVED:\t", resp)
    while decode_socket(resp) != "069 | 04 10 10 10 10 10 10 10":
        resp = kin_socketcan.decode_frame(msg)
        print("RECEIVED:\t", resp)

    print("code data size received")
    print("ready to start sending hex")
    # start reading and writing the binary file here
    

    hexUtil = HexUtility()
    hexUtil.open_file("/home/geffen.cooper/Desktop/kinetek_scripts/hex_file_copies/2.28_copy.hex")
    print(hexUtil.get_file_data_size())
    print(hexUtil.get_total_checksum())
    print(hexUtil.get_page_checksums())
    write_ids = [0x04F, 0x050, 0x051, 0x052]

    i = 0
    while True:
        data = hexUtil.get_next_data_8()
        if data == -1:
            break

        msg = make_socketcan_packet(write_ids[i],data)
        print("SENT:\t",msg)
        resp = kin_socketcan.decode_frame(msg)
        if resp != None:
            print("RECEIVED:\t", resp)

        i += 1
        if i == len(write_ids):
            i = 0
        
    print(kin_socketcan.hex_data)
    # print(make_socketcan_packet(0x04F,hexUtil.get_next_data_8()))
    # print(make_socketcan_packet(0x050,hexUtil.get_next_data_8()))
    # print(make_socketcan_packet(0x051,hexUtil.get_next_data_8()))
    # print(make_socketcan_packet(0x052,hexUtil.get_next_data_8()))
    
        
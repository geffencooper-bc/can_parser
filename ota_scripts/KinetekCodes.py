from HexUtility import make_socketcan_packet, data_string_to_byte_list

# FW_REVISION_REQUEST = make_socketcan_packet(0x045, data_string_to_byte_list("00 00 00 00 00 00 00 00"))
# ENTER_IAP_MODE_REQUEST = make_socketcan_packet(0x048, data_string_to_byte_list("00 00 00 00 00 00 00 00"))
# SEND_BYTES_REQUEST = make_socketcan_packet(0x048, data_string_to_byte_list("88 88 88 88 88 88 88 88"))

ENTER_IAP_MODE_RESPONSE = "060 | 80 00 00 00 00"

# used for decoding requests/responses
IAP_data_lookup = [

    ('069 | 10 10 10 10 10 10 10 10' ,                                                            "RECEIVED_32__BYTES"),
    ('069 | 99 99 99 99 99 99 99 99' ,                                                            "SEND_BYTES_RESPONSE"),
    ('067 | [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 5E|5F [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] 00 00 00' , "FW_REVISION_REQUEST_RESPONSE"),
    ('069 | 02 10 10 10 10 10 10 10' ,                                                            "SEND_CODE_START_ADDRESS_RESPONSE"),
    ('069 | 03 10 10 10 10 10 10 10' ,                                                            "SEND_CODE_CHECKSUM_DATA_RESPONSE"),
    ('069 | 04 10 10 10 10 10 10 10' ,                                                            "SEND_CODE_DATA_SIZE_RESPONSE"),
    ('069 | 05 20 20 20 20 20 20 20' ,                                                            "CALCULATE_CHECKSUM_RESPONSE"),
    ('069 | 07 40 40 40 40 40 40 40' ,                                                            "CALCULATE_PAGE_CHECKSUM_RESPONSE"),
    ('84 [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F] [0-9A-F][0-9A-F]',                    "calculated page checksum")
] 

# find the according pattern in the above table
def lookup(self,data, table):
    for pattern, value in table:
        if re.search(pattern, data):
            return value
    return ""

def get_kinetek_can_id_code(arg):
    return{
        'FW_REVISION_REQUEST':   0x045,
        'IAP_REQUEST':           0x048,
        'SEND_PACKET_1':         0x04F,
        'SEND_PACKET_2':         0x050,
        'SEND_PACKET_3':         0x051,
        'SEND_PACKET_4':         0x052,
        'RESEND_PACKET_1':       0x053,
        'RESEND_PACKET_2':       0x054,
        'RESEND_PACKET_3':       0x055,
        'RESEND_PACKET_4':       0x056
    }.get(arg)

def get_kinetek_data_code(arg):
    return{
        "DEFAULT":              '00 00 00 00 00 00 00 00',
        "ENTER_IAP_MODE":       '00 00 00 00 00 00 00 00',
        "SEND_BYTES":           '88 88 88 88 88 88 88 88',
        "CODE_START_ADDRESS_PREFIX":    '02 ',
        "CODE_START_ADDRESS_SUFFIX":    ' 9A 00 00',
        "SEND_CHECKSUM_PREFIX":         '03 ',
        "SEND_CHECKSUM_SUFFIX":         ' 9B 00 00',  
        "SEND_DATA_SIZE_PREFIX":        '04 ',
        "SEND_DATA_SIZE_SUFFIX":        ' 9C 00 00',
        "END_OF_HEX_FILE":      '05 10 10 10 10 10 10 10',
        "CHECK_CHECK_SUM":      '06 __ __ __ __ 9D __ __',
        "PAGE_CHECKSUM_DATA":   '07 __ __ __ __ 9E __ __'
    }.get(arg)
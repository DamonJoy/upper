from CanDriver import *
from DataClass import *

class CanAddress(Enum):
    pc = 0x65
    dcboard = 0xA0

class CanProtocol():
    def __init__(self):
        pass

    def send_read_version_command(self, candevice, channel, type_key):
        type = FrameType.extern
        id = 0x19F40000 | (CanAddress.dcboard.value << 8) | CanAddress.pc.value
        byte0 = 0xFF    # 全部包一起上报
        if('software' == type_key):
            byte1 = 0x01
        elif('hardware' == type_key):
            byte1 = 0x02
        elif ('pcb_sn' == type_key):
            byte1 = 0x03
        elif ('productname' == type_key):
            byte1 = 0x04
        elif ('module_sn' == type_key):
            byte1 = 0x05
        else:
            return False
        databyte = [byte0, byte1, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        message = {'type': type, 'id': id, 'databyte': databyte}
        #candevice.sendmessage(channel, message)
        candevice.add_a_message_to_send_buff(message)


    def send_write_parameter_command(self, candevice, channel, mode, para_addr, para_value):
        type = FrameType.extern
        id = 0x19F10000 | (CanAddress.dcboard.value << 8) | CanAddress.pc.value
        byte0 = 0x01    # 设置命令
        byte1 = (para_addr >> 8) & 0xFF     # 地址高字节
        byte2 = (para_addr >> 0) & 0xFF     # 地址低字节
        byte3 = (para_value >> 8) & 0xFF    # 参数值高字节
        byte4 = (para_value >> 0) & 0xFF    # 参数值低字节
        if(WriteParameterMode.write_ram == mode):
            byte5 = 0xAA
        else:
            byte5 = 0x55
        byte6 = 0xFF
        byte7 = 0xFF
        databyte = [byte0, byte1, byte2, byte3, byte4, byte5, byte6, byte7]
        message = {'type': type, 'id': id, 'databyte': databyte}
        #candevice.sendmessage(channel, message)
        candevice.add_a_message_to_send_buff(message)


    def send_read_parameter_command(self, candevice, channel, para_addr, para_num):
        if(0 >= para_num):
            return False
        if(2<para_num):
            para_num = 2

        type = FrameType.extern
        id = 0x19F00000 | (CanAddress.dcboard.value << 8) | CanAddress.pc.value
        byte0 = (para_addr >> 8) & 0xFF     # 地址高字节
        byte1 = (para_addr >> 0) & 0xFF     # 地址低字节
        byte2 = (para_num >> 8) & 0xFF      # 参数个数高字节
        byte3 = (para_num >> 0) & 0xFF      # 参数个数低字节
        databyte = [byte0, byte1, byte2, byte3, 0xFF, 0xFF, 0xFF, 0xFF]
        message = {'type': type, 'id': id, 'databyte': databyte}
        #candevice.sendmessage(channel, message)
        candevice.add_a_message_to_send_buff(message)


    def send_read_public_data_command(self, candevice, channel, data_type, data_addr, data_num):
        type = FrameType.extern
        id = 0x19F20000 | (CanAddress.dcboard.value << 8) | CanAddress.pc.value
        byte0 = data_type                    # 公共数据类型
        byte1 = (data_addr >> 8) & 0xFF      # 公共数据地址高字节
        byte2 = (data_addr >> 0) & 0xFF      # 公共数据地址低字节
        byte3 = data_num                     # 公共数据个数
        databyte = [byte0, byte1, byte2, byte3, 0xFF, 0xFF, 0xFF, 0xFF]
        message = {'type': type, 'id': id, 'databyte': databyte}
        #candevice.sendmessage(channel, message)
        candevice.add_a_message_to_send_buff(message)


    def send_write_transparent_mode_command(self, candevice, channel, target_canaddr, mode):
        type = FrameType.extern
        id = 0x18FF0000 | (target_canaddr << 8) | 0xFF
        byte0 = 0xF8  # 命令码
        byte1 = mode  # 进入/退出透传
        databyte = [byte0, byte1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = {'type': type, 'id': id, 'databyte': databyte}
        #candevice.sendmessage(channel, message)
        candevice.add_a_message_to_send_buff(message)



'''
import threading
def thread_send_command():
    while True:
        time.sleep(0.05)
        protocol.send_read_version_command(can_device, can_channel, 'software')
        protocol.send_write_parameter_command(candevice=can_device, channel=can_channel,
                                              mode=WriteParameterMode.write_ram_eeprom, para_addr=15, para_value=16)
        protocol.send_read_parameter_command(candevice=can_device, channel=can_channel, para_addr=15, para_num=1)
        protocol.send_read_public_data_command(candevice=can_device, channel=can_channel,
                                               data_type=0, data_addr=3, data_num=1)


def thread_analyze_data():
    while True:
        time.sleep(0.05)
        rcv_num, message_list = can_device.getmessage(can_channel)
        if (rcv_num > 0):
            protocol.analyze_received_dcboard_candata(rcv_num, message_list)


can_device = CanDevice(device_type=4, device_index=1, baudrate=250)
can_channel = CanChannel.channel1
common_data = DcboardCommonData()
version_data = DcboardVersionData()
public_data = DcboardPublicData()
parameter = DcboardParameter()
protocol = CanProtocol(common_data, version_data, public_data, parameter)

a = threading.Thread(target=thread_send_command)
a.start()
thread_analyze_data()
'''

'''
g_can_device = CanDevice(device_type=4, device_index=0, baudrate=250)
g_can_channel = CanChannel.channel1
common_data = DcboardCommonData(0)
version_data = DcboardVersionData()
public_data = DcboardPublicData()
parameter = DcboardParameter()
protocol = CanProtocol(common_data, version_data, public_data, parameter)

a = threading.Thread(target=analyze_can_data)
a.start()
while 1:
    time.sleep(0.5)
    bytes = protocol.read_dcboard_version(g_can_device, g_can_channel, 'software')
    if(False != bytes):
        str = ''.join('%s' %id for id in bytes)
        #print(str)
'''




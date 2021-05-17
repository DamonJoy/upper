import time
from ctypes import *
from enum import Enum

class VCI_INIT_CONFIG(Structure):
    """ 定义类（结构体数据类型），以便调用dll库中的C函数，类继承自ctypes模块 """
    _fields_ = [("AccCode", c_uint),
                ("AccMask", c_uint),
                ("Reserved", c_uint),
                ("Filter", c_ubyte),
                ("Timing0", c_ubyte),
                ("Timing1", c_ubyte),
                ("Mode", c_ubyte)
                ]

class VCI_CAN_OBJ(Structure):
    _fields_ = [("ID", c_uint),
                ("TimeStamp", c_uint),
                ("TimeFlag", c_ubyte),
                ("SendType", c_ubyte),
                ("RemoteFlag", c_ubyte),
                ("ExternFlag", c_ubyte),
                ("DataLen", c_ubyte),
                ("Data", c_ubyte*8),
                ("Reserved", c_ubyte*3)
                ]

class CanChannel(Enum):
    channel1 = 0
    channel2 = 1    # 0为通道1，1为通道2 (和can盒的dll库对应)

class FrameType(Enum):
    standard = 0
    extern = 1      # 0为标准帧，1为扩展帧 (和can盒的dll库对应)

class CanDevice():
    #def __init__(self, device_type, device_index, baudrate):
    def __init__(self):
        self.device_type = 4          # 设备的类型号，由厂家定义（创世科技的CAN盒，类型号为 4）
        self.device_index = 0        # 设备索引，0表示第1个设备，1表示第2个设备，以此类推
        self.baudrate = 250                # CAN波特率： 100K，125K，200K, 250K, 400K, 500K, 666K, 800K, 1000K
        self.can_dll_Name = './ControlCAN.dll'
        self.can_dll = 'void'
        self.rcv_messagelist = []
        self.send_messagelist = []
        self.rcv_interval_ms = 100
        self.send_interval_ms = 1
        # self.init_ok_flag = False
        #self.init()

    def init(self):
        """初始化CAN设备"""
        self.can_dll = windll.LoadLibrary(self.can_dll_Name)
        status_ok = 1
        self.closedevice()
        ret = self.can_dll.VCI_OpenDevice(self.device_type, self.device_index, 0)  # 参数：设备类型，设备索引，保留参数设为0
        if ret == status_ok:
            #print('调用 VCI_OpenDevice成功\r')
            pass
        else:
            #print('调用 VCI_OpenDevice出错\r')
            return False

        if self.baudrate == 100:        # 波特率100k
            timing0 = 0x04
            timing1 = 0x1C
        elif self.baudrate == 125:      # 波特率125k
            timing0 = 0x81
            timing1 = 0xFA
        elif self.baudrate == 200:      # 波特率200k
            timing0 = 0x03
            timing1 = 0x1C
        elif self.baudrate == 250:      # 波特率250k
            timing0 = 0x01
            timing1 = 0x1C
        elif self.baudrate == 400:      # 波特率400k
            timing0 = 0x80
            timing1 = 0xFA
        elif self.baudrate == 500:      # 波特率500k
            timing0 = 0x00
            timing1 = 0x1C
        elif self.baudrate == 666:      # 波特率666k
            timing0 = 0x80
            timing1 = 0xB6
        elif self.baudrate == 800:      # 波特率800k
            timing0 = 0x00
            timing1 = 0x16
        elif self.baudrate == 1000:     # 波特率1000k
            timing0 = 0x00
            timing1 = 0x14
        else:
            print('异常的波特率！\r')
            return False
        acc_mask = 0xFFFFFFFF  # 和acc_code, message_id高bit对齐，bit为0表示打开此bit对应的acc_code的bit匹配功能
        acc_code = 0b11110100011110001011010110011000  # 和message_id高bit对齐, 若某bit的匹配功能被acc_mask打开, 则和message_id进行bit匹配
        filter = 0  # 0/1:接收标准帧和扩展帧， 2:只接收标准帧, 3:只接收扩展帧
        reserved = 0
        mode = 0  # 0:正常工作， 1:仅监听模式
        vci_initconfig = VCI_INIT_CONFIG(acc_code, acc_mask, reserved, filter, timing0, timing1, mode)

        # 初始1通道
        ret = self.can_dll.VCI_InitCAN(self.device_type, self.device_index, CanChannel.channel1.value, byref(vci_initconfig))
        if ret == status_ok:
            #print('调用 VCI_InitCAN1成功\r')
            pass
        else:
            #print('调用 VCI_InitCAN1出错\r')
            return False
        ret = self.can_dll.VCI_StartCAN(self.device_type, self.device_index, CanChannel.channel1.value)
        if ret == status_ok:
            #print('调用 VCI_StartCAN1成功\r')
            pass
        else:
            #print('调用 VCI_StartCAN1出错\r')
            return False

        # 初始2通道
        ret = self.can_dll.VCI_InitCAN(self.device_type, self.device_index, CanChannel.channel2.value, byref(vci_initconfig))
        if ret == status_ok:
            #print('调用 VCI_InitCAN2 成功\r')
            pass
        else:
            #print('调用 VCI_InitCAN2 出错\r')
            return False
        ret = self.can_dll.VCI_StartCAN(self.device_type, self.device_index, CanChannel.channel2.value)
        if ret == status_ok:
            #print('调用 VCI_StartCAN2 成功\r')
            pass
        else:
            #print('调用 VCI_StartCAN2 出错\r')
            return False
        #self.init_ok_flag = True
        return True


    def sendmessage(self, channel, message):
        """发送一帧报文"""
        #if (True != self.init_ok_flag):
            #return False
        if((CanChannel.channel1 != channel) and (CanChannel.channel2 != channel)):
            return False
        if(False == isinstance(message, dict)):
            return False
        if(('type' not in message.keys()) or ('id' not in message.keys()) or ('databyte' not in message.keys())):
            return False
        # 组帧
        ubyte_array = c_ubyte * 8
        data = ubyte_array(message['databyte'][0], message['databyte'][1], message['databyte'][2], message['databyte'][3],
                        message['databyte'][4], message['databyte'][5], message['databyte'][6], message['databyte'][7])
        ubyte_3array = c_ubyte * 3
        reserved = ubyte_3array(0, 0, 0)       # 有3Bytes为保留参数
        time_stamp = 0
        time_flag = 0       # 不使用时间标识
        send_type = 0       # 0:自动重发， 1:单次发送
        remote_flag = 0     # 非远程帧(即是数据帧),
        data_len = 8        # 数据长度
        vci_can_obj = VCI_CAN_OBJ(message['id'], time_stamp, time_flag, send_type,
                                  remote_flag, message['type'].value, data_len, data, reserved)

        # 发送组好的帧
        status_ok = 1
        frame_len = 1   # 发送一帧
        ret = self.can_dll.VCI_Transmit(self.device_type, self.device_index, channel.value,
                                        byref(vci_can_obj), frame_len)
        if ret == status_ok:
            return True
        else:
            return False


    def add_a_message_to_send_buff(self, message):
        self.send_messagelist.append(message)


    def copy_device_data_to_rcv_buff(self, channel):
        """获取CAN报文"""
        #if(True != self.init_ok_flag):
            #return False
        data_buff = (VCI_CAN_OBJ * 2500)()    # 结构体数组 data_buff 用来保存读到的各帧报文
        frame_len = 2500
        wait_time = 0
        rcv_num = self.can_dll.VCI_Receive(self.device_type, self.device_index, channel.value,
                                           byref(data_buff[0]), frame_len, wait_time)
        if(-1 == rcv_num):
            self.closedevice()
            self.init()
            return False
        #self.can_dll.VCI_ClearBuffer(self.device_type, self.device_index, channel.value) # 清空CAN盒的接收Buffer和发送Buffer
        for i in range(rcv_num):
            if(FrameType.standard.value == data_buff[i].ExternFlag):
                type = FrameType.standard    # type, 0:标准帧， 1:扩展帧
            else:
                type = FrameType.extern
            message_dict = {'type': type, 'id': data_buff[i].ID, 'databyte': list(data_buff[i].Data)}
            self.rcv_messagelist.append(message_dict)


    def closedevice(self):
        """关闭设备"""
        ret = self.can_dll.VCI_CloseDevice(self.device_type, self.device_index)
        if(1 == ret):
            return True
        else:
            return False


'''
device1 = CanDevice(device_type=4, device_index=1, baudrate=250)
for i in range(20):
    message = {'type': FrameType.extern, 'id': 0x19F2A065, 'databyte': [0, 0, 0, 0, 0, 0, 0, i]}
    device1.add_a_message_to_send_buff(message)
message = {'type': FrameType.extern, 'id': 0x19F2A065, 'databyte': [0, 0, 0, 0, 0, 0, 0, i]}
while True:
    ret = device1.sendmessage(CanChannel.channel1, message)
    #print(ret)
'''

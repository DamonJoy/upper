from enum import Enum

class WriteParameterMode(Enum):   # 设置参数的模式, 和协议对应
    write_ram = 0xAA
    write_ram_eeprom = 0x55

class CommonDataStructure():
    def __init__(self, widget=None):
        self.received_value = None
        self.widget = widget
        self.update_flag = None

class VersionDataStructure():
    def __init__(self, widget=None):
        self.version_str = ''
        self.read_ok_flag = None         # None：没读， False:已发送读命令，正在等待接收响应，True：读成功 (4个包全收到才成功)
        self.package_list = []        # 接收到的包列表，DC板会固定发4包，每包有6个ASCII码
        self.widget = widget
        self.update_flag = None

class PublicDataStructure():
    def __init__(self, type, addr, widget=None):
        self.type = type
        self.addr = addr
        self.read_value = None
        self.write_value = None
        self.read_ok_flag = None         # None：没读， False:读失败， True：读成功
        self.write_ok_flag = None        # None：没写， False:写失败， True：写成功
        self.widget = widget
        self.update_flag = None

class ParameterStructure():
    def __init__(self, addr, widget=None):
        self.addr = addr
        self.read_value = None
        self.write_value = None
        self.write_mode = WriteParameterMode.write_ram
        self.read_ok_flag = None  # None：没读， False:读失败， True：读成功
        self.write_ok_flag = None  # None：没写， False:写失败， True：写成功
        self.widget = widget
        self.update_flag = None

class DcboardCommonData():
    def __init__(self):

        self.data = {
                'boardstate': CommonDataStructure(),
                'alarmlevel': CommonDataStructure(),
                'relayk1state': CommonDataStructure(),
                'relayk2state': CommonDataStructure(),
                'reverseflag': CommonDataStructure(),
                'alarm_bms_offline': CommonDataStructure(),
                'alarm_mos_overtemp': CommonDataStructure(),
                'alarm_loadend_overvolt': CommonDataStructure(),
                'alarm_loadend_undervolt': CommonDataStructure(),
                'alarm_batteryend_overvolt': CommonDataStructure(),
                'alarm_batteryend_undervolt': CommonDataStructure(),
                'alarm_loadend_overchargecurrent': CommonDataStructure(),
                'alarm_loadend_overdischargecurrent': CommonDataStructure(),
                'alarm_batteryend_overchargecurrent': CommonDataStructure(),
                'alarm_batteryend_overdischargecurrent': CommonDataStructure(),
                'pcbtemp': CommonDataStructure(),
                'mostemp1': CommonDataStructure(),
                'mostemp2': CommonDataStructure(),
                'loadend_volt': CommonDataStructure(),
                'loadend_current': CommonDataStructure(),
                'batteryend_volt': CommonDataStructure(),
                'batteryend_current': CommonDataStructure()
            }
        '''
        self.data = {
             'boardstate': CommonDataStructure(widget = ui.label_boardstate),
            'alarmlevel': CommonDataStructure(widget = ui.qlcd_alarmlevel),
            'relayk1state': CommonDataStructure(widget = ui.label_relay1state),
            'relayk2state': CommonDataStructure(widget = ui.label_relay2state),
            'reverseflag': CommonDataStructure(widget = ui.label_reversestate),
            'alarm_bms_offline': CommonDataStructure(widget = ui.qlabel_bms_offline_alarm),
            'alarm_mos_overtemp': CommonDataStructure(widget = ui.qlabel_mos_overtemp_alarm),
            'alarm_loadend_overvolt': CommonDataStructure(widget = ui.qlabel_loadend_overvolt_alarm),
            'alarm_loadend_undervolt': CommonDataStructure(widget = ui.qlabel_loadend_undervolt_alarm),
            'alarm_batteryend_overvolt': CommonDataStructure(widget = ui.qlabel_battend_overvolt_alarm),
            'alarm_batteryend_undervolt': CommonDataStructure(widget = ui.qlabel_battend_undervolt_alarm),
            'alarm_loadend_overchargecurrent': CommonDataStructure(widget = ui.qlabel_loadend_chgovercurrent_alarm),
            'alarm_loadend_overdischargecurrent': CommonDataStructure(widget = ui.qlabel_loadend_dsgovercurrent_alarm),
            'alarm_batteryend_overchargecurrent': CommonDataStructure(widget = ui.qlabel_battend_chgovercurrent_alarm),
            'alarm_batteryend_overdischargecurrent': CommonDataStructure(widget = ui.qlabel_battend_dsgovercurrent_alarm),
            'pcbtemp': CommonDataStructure(ui.qlcd_pcbtemp),
            'mostemp1': CommonDataStructure(ui.qlcd_mostemp1),
            'mostemp2': CommonDataStructure(ui.qlcd_mostemp2),
            'loadend_volt': CommonDataStructure(ui.qlcd_loadend_volt),
            'loadend_current': CommonDataStructure(ui.qlcd_loadend_current),
            'batteryend_volt': CommonDataStructure(ui.qlcd_batteryend_volt),
            'batteryend_current': CommonDataStructure(ui.qlcd_batteryend_current)
        }
        '''


    def set_data(self, data_key, data_value):
        if(data_key not in self.data.keys()):
            return False
        if(data_value == self.data[data_key].received_value):
            return False
        self.data[data_key].received_value = data_value
        self.data[data_key].update_flag = True
        return True


    def init_data(self):
        for key in self.data:
            self.data[key].received_value = None

class DcboardVersionData():
    def __init__(self):
        self.package_len = 4  # 版本号包含在4个包中,每个包有6个Bytes
        self.data = {
            'software':VersionDataStructure(),
            'hardware': VersionDataStructure(),
            'pcb_sn': VersionDataStructure(),
            'productname': VersionDataStructure(),
            'module_sn': VersionDataStructure(),
        }


    def set_version(self, data_key, str):
        if(data_key not in self.data.keys()):
            return
        length = len(str)
        if(length < 24):
            cnt = 24 - length
            for i in range(cnt):
                str = str + ' '

        for i in range(24):
            self.data[data_key].bytes[i] = ord(str[i])


    def init_data(self):
        for key in self.data:
            self.version_str = ''
            self.data[key].read_ok_flag = None
            self.package_list = []



class DcboardPublicData():
    def __init__(self):
        self.__receivedbmsdata_type = 0
        self.__receivedbmsdata_startaddr = 0
        self.__receivedbmsdata_endaddr = 16
        self.receivedbmsdata = {
            'controlcommand' : PublicDataStructure(type=0, addr=3),
            'setworkmode' : PublicDataStructure(type=0, addr=4),
            'controlmainrelaycommand' : PublicDataStructure(type=0, addr=5),
            'max_chargeablecurrent' : PublicDataStructure(type=0, addr=6),
            'max_chargeablevolt' : PublicDataStructure(type=0, addr=7),
            'max_dischargeablecurrent' : PublicDataStructure(type=0, addr=8),
            'min_dischargeablevolt' : PublicDataStructure(type=0, addr=9),
            'target_raiseddischargevolt' : PublicDataStructure(type=0, addr=10),
            'leadacid_eodvolt' : PublicDataStructure(type=0, addr=11),
            'charger_maxchargevolt' : PublicDataStructure(type=0, addr=12),
            'min_raiseddischargevolt' : PublicDataStructure(type=0, addr=13),
            'lithiumfirst_leadacidchargevolt' : PublicDataStructure(type=0, addr=14),
            'leadacidfirst_reductiondischargevolt' : PublicDataStructure(type=0, addr=15),
            'lithiumfirst_maxdischargeablevolt' : PublicDataStructure(type=0, addr=16)
        }
        self.__versiondata_type = 4
        self.__versiondata_startaddr = 0
        self.__versiondata_endaddr = 0
        self.versiondata = {
            'hardwareversion' : PublicDataStructure(type=4, addr=0)   # Dcboard的IO口定义的硬件版本
        }

    def get_receivedbmsdata_type(self):
        return self.__receivedbmsdata_type

    def get_receivedbmsdata_startaddr(self):
        return self.__receivedbmsdata_startaddr

    def get_receivedbmsdata_endaddr(self):
        return self.__receivedbmsdata_endaddr

    def get_versiondata_type(self):
        return self.__versiondata_type

    def get_versiondata_startaddr(self):
        return self.__versiondata_startaddr

    def get_versiondata_endaddr(self):
        return self.__versiondata_endaddr


    def set_public_data(self, type, addr, read_value=None, write_value=None, read_ok_flag='NA', write_ok_flag='NA'):
        target_data = None
        if (self.get_receivedbmsdata_type() == type):
            if((self.get_receivedbmsdata_startaddr() <= addr) and (self.get_receivedbmsdata_endaddr() >= addr)):
                for key in self.receivedbmsdata:
                    if (addr == self.receivedbmsdata[key].addr):
                        target_data = self.receivedbmsdata[key]
                        break
        elif (self.get_versiondata_type() == type):
            if((self.get_versiondata_startaddr() <= addr) and (self.get_versiondata_endaddr() >= addr)):
                for key in self.versiondata:
                    if (addr == self.versiondata[key].addr):
                        target_data = self.versiondata[key]
                        break
        if(None != target_data):
            if (None != read_value):
                target_data.read_value = read_value
            if (None != write_value):
                target_data.write_value = write_value
            if ((None == read_ok_flag) or (True == read_ok_flag) or (False == read_ok_flag)):
                target_data.read_ok_flag = read_ok_flag
            if ((None == write_ok_flag) or (True == write_ok_flag) or (False == write_ok_flag)):
                target_data.write_ok_flag = write_ok_flag
            return True
        return False


    def get_public_data(self, type, addr):
        if (self.get_receivedbmsdata_type() == type):
            if((self.get_receivedbmsdata_startaddr() <= addr) and (self.get_receivedbmsdata_endaddr() >= addr)):
                for key in self.receivedbmsdata:
                    if (addr == self.receivedbmsdata[key].addr):
                        return self.receivedbmsdata[key]
        elif (self.get_versiondata_type() == type):
            if((self.get_versiondata_startaddr() <= addr)
              and (self.get_versiondata_endaddr() >= addr)):
                for key in self.versiondata:
                    if (addr == self.versiondata[key].addr):
                        return self.versiondata[key]
        return False


    def init_data(self):
        for key in self.receivedbmsdata:
            self.receivedbmsdata[key].read_value = None
            self.receivedbmsdata[key].write_value = None
            self.receivedbmsdata[key].read_ok_flag = None
            self.receivedbmsdata[key].write_ok_flag = None
        for key in self.versiondata:
            self.versiondata[key].read_value = None
            self.versiondata[key].write_value = None
            self.versiondata[key].read_ok_flag = None
            self.versiondata[key].write_ok_flag = None



class DcboardParameter():
    def __init__(self):
        # 校准参数
        self.__calibrate_para_startaddr = 15
        self.calibrate_para = {
            'batteryend_totalvolt_k': ParameterStructure(addr=self.__calibrate_para_startaddr),
            'batteryend_totalvolt_b': ParameterStructure(addr=self.__calibrate_para_startaddr + 1),
            'loadend_totalvolt_k': ParameterStructure(addr=self.__calibrate_para_startaddr + 2),
            'loadend_totalvolt_b': ParameterStructure(addr=self.__calibrate_para_startaddr + 3),
            'batteryend_chargecurrent_k': ParameterStructure(addr=self.__calibrate_para_startaddr + 4),
            'batteryend_chargecurrent_b': ParameterStructure(addr=self.__calibrate_para_startaddr + 5),
            'batteryend_dischargecurrent_k': ParameterStructure(addr=self.__calibrate_para_startaddr + 6),
            'batteryend_dischargecurrent_b': ParameterStructure(addr=self.__calibrate_para_startaddr + 7),
            'loadend_chargecurrent_k': ParameterStructure(addr=self.__calibrate_para_startaddr + 8),
            'loadend_chargecurrent_b': ParameterStructure(addr=self.__calibrate_para_startaddr + 9),
            'loadend_dischargecurrent_k': ParameterStructure(addr=self.__calibrate_para_startaddr + 10),
            'loadend_dischargecurrent_b': ParameterStructure(addr=self.__calibrate_para_startaddr + 11)
        }
        self.__calibrate_para_endaddr = self.__calibrate_para_startaddr + 11

        # 序列号参数
        self.__version_para_startaddr = 40
        self.version_para = {
            'pcb_serialnumber_byte1_2' : ParameterStructure(addr=self.__version_para_startaddr),  # 例：0x564D，对应VM
            'pcb_serialnumber_byte3_4' : ParameterStructure(addr=self.__version_para_startaddr + 1),
            'pcb_serialnumber_byte5_6' : ParameterStructure(addr=self.__version_para_startaddr + 2),
            'pcb_serialnumber_byte7_8' : ParameterStructure(addr=self.__version_para_startaddr + 3),
            'pcb_serialnumber_byte9_10' : ParameterStructure(addr=self.__version_para_startaddr + 4),
            'pcb_serialnumber_byte11_12' : ParameterStructure(addr=self.__version_para_startaddr + 5),
            'pcb_serialnumber_byte13_14' : ParameterStructure(addr=self.__version_para_startaddr + 6),
            'pcb_serialnumber_byte15_16' : ParameterStructure(addr=self.__version_para_startaddr + 7),
            'pcb_serialnumber_byte17_18' :ParameterStructure(addr=self.__version_para_startaddr + 8),
            'pcb_serialnumber_byte19_20' : ParameterStructure(addr=self.__version_para_startaddr + 9),
            'pcb_serialnumber_byte21_22' : ParameterStructure(addr=self.__version_para_startaddr + 10),
            'pcb_serialnumber_byte23_24' : ParameterStructure(addr=self.__version_para_startaddr + 11),
            'module_serialnumber_byte1_2' : ParameterStructure(addr=self.__version_para_startaddr + 12),  # 例：0x564D，对应VM
            'module_serialnumber_byte3_4': ParameterStructure(addr=self.__version_para_startaddr + 13),
            'module_serialnumber_byte5_6' : ParameterStructure(addr=self.__version_para_startaddr + 14),
            'module_serialnumber_byte7_8' : ParameterStructure(addr=self.__version_para_startaddr + 15),
            'module_serialnumber_byte9_10' : ParameterStructure(addr=self.__version_para_startaddr + 16),
            'module_serialnumber_byte11_12' : ParameterStructure(addr=self.__version_para_startaddr + 17),
            'module_serialnumber_byte13_14' : ParameterStructure(addr=self.__version_para_startaddr + 18),
            'module_serialnumber_byte15_16' : ParameterStructure(addr=self.__version_para_startaddr + 19),
            'module_serialnumber_byte17_18' : ParameterStructure(addr=self.__version_para_startaddr + 20),
            'module_serialnumber_byte19_20' : ParameterStructure(addr=self.__version_para_startaddr + 21),
            'module_serialnumber_byte21_22' : ParameterStructure(addr=self.__version_para_startaddr + 22),
            'module_serialnumber_byte23_24' : ParameterStructure(addr=self.__version_para_startaddr + 23)
        }
        self.__version_para_endaddr = self.__version_para_startaddr + 23

        # 告警参数
        self.__alarm_para_startaddr = 2000
        self.alarm_para = {
            'alarm_loadend_overvolt' : self.__generate_alarmobject(start_addr=self.__alarm_para_startaddr),
            'alarm_loadend_undervolt' : self.__generate_alarmobject(start_addr=self.__alarm_para_startaddr + 9 * 1),
            'alarm_batteryend_overvolt' : self.__generate_alarmobject(start_addr=self.__alarm_para_startaddr + 9 * 2),
            'alarm_batteryend_undervolt' : self.__generate_alarmobject(start_addr=self.__alarm_para_startaddr + 9 * 3),
            'alarm_loadend_overchargecurrent' : self.__generate_alarmobject(start_addr=self.__alarm_para_startaddr + 9 * 4),
            'alarm_loadend_overdischargecurrent' : self.__generate_alarmobject( start_addr=self.__alarm_para_startaddr + 9 * 5),
            'alarm_batteryend_overchargecurrent' : self.__generate_alarmobject(start_addr=self.__alarm_para_startaddr + 9 * 6),
            'alarm_batteryend_overdischargecurrent' : self.__generate_alarmobject(start_addr=self.__alarm_para_startaddr + 9 * 7),
            'alarm_system_overtemp' : self.__generate_alarmobject(start_addr=self.__alarm_para_startaddr + 9 * 8),
            'alarm_bmsoffline' : self.__generate_alarmobject(start_addr=self.__alarm_para_startaddr + 9 * 9),
            'alarm_reverse' : self.__generate_alarmobject(start_addr=self.__alarm_para_startaddr + 9 * 10),
            'alarm_mos1_overtemp' : self.__generate_alarmobject(start_addr=self.__alarm_para_startaddr + 9 * 11),
            'alarm_mos2_overtemp' : self.__generate_alarmobject(start_addr=self.__alarm_para_startaddr + 9 * 12)
        }
        self.__alarm_para_endaddr = self.__alarm_para_startaddr + 9*12


    def __generate_alarmobject(self, start_addr):
        alarm = {'二级告警':
                     {'阈值': ParameterStructure(addr=start_addr),
                      '回差值': ParameterStructure(addr=start_addr + 1),
                      '告警延时': ParameterStructure(addr=start_addr + 2),
                      '恢复延时': ParameterStructure(addr=start_addr + 3),
                      },
                 '一级告警':
                     {'阈值': ParameterStructure(addr=start_addr + 4),
                      '回差值': ParameterStructure(addr=start_addr + 5),
                      '告警延时': ParameterStructure(addr=start_addr + 6),
                      '恢复延时': ParameterStructure(addr=start_addr + 7),
                      },
                 '显示告警': {'显示级别': ParameterStructure(addr=start_addr + 8)}
                 }
        return alarm


    def get_calibrate_para_startaddr(self):
        return self.__calibrate_para_startaddr


    def get_calibrate_para_endaddr(self):
        return self.__calibrate_para_endaddr


    def get_version_para_startaddr(self):
        return self.__version_para_startaddr


    def get_version_para_endaddr(self):
        return self.__version_para_endaddr


    def get_alarm_para_startaddr(self):
        return self.__alarm_para_startaddr


    def get_alarm_para_endaddr(self):
        return self.__alarm_para_endaddr


    def set_parameter(self, addr, read_value=None, write_value=None, write_mode=None, read_ok_flag='NA', write_ok_flag='NA'):
        target_parameter = None
        if ((self.get_calibrate_para_startaddr() <= addr) and (self.get_calibrate_para_endaddr() >= addr)):
            for key in self.calibrate_para:
                if (addr == self.calibrate_para[key].addr):
                    target_parameter = self.calibrate_para[key]
        elif ((self.get_version_para_startaddr() <= addr) and (self.get_version_para_endaddr() >= addr)):
            for key in self.version_para:
                if (addr == self.version_para[key].addr):
                    target_parameter = self.version_para[key]
        elif ((self.get_alarm_para_startaddr() <= addr) and (self.get_alarm_para_endaddr() >= addr)):
            for key0 in self.alarm_para:
                for key1 in self.alarm_para[key0]:
                    for key2 in self.alarm_para[key0][key1]:
                        if (addr == self.alarm_para[key0][key1][key2].addr):
                            target_parameter = self.alarm_para[key0][key1][key2]
                            break
                    if(None != target_parameter):
                        break
                if (None != target_parameter):
                    break
        if(None != target_parameter):
            if (None != read_value):
                target_parameter.read_value = read_value
            if (None != write_value):
                target_parameter.write_value = write_value
            if ((WriteParameterMode.write_ram == write_mode) or (WriteParameterMode.write_ram_eeprom == write_mode)):
                target_parameter.write_mode = write_mode
            if ((None == read_ok_flag) or (True == read_ok_flag) or (False == read_ok_flag)):
                target_parameter.read_ok_flag = read_ok_flag
            if ((None == write_ok_flag) or (True == write_ok_flag) or (False == write_ok_flag)):
                target_parameter.read_ok_flag = write_ok_flag
            return True
        return False


    def get_parameter(self, addr):
        if ((self.get_calibrate_para_startaddr() <= addr)
                and (self.get_calibrate_para_endaddr() >= addr)):
            for key in self.calibrate_para:
                if (addr == self.calibrate_para[key].addr):
                    return self.calibrate_para[key]
        elif ((self.get_version_para_startaddr() <= addr)
              and (self.get_version_para_endaddr() >= addr)):
            for key in self.version_para:
                if (addr == self.version_para[key].addr):
                    return self.version_para[key]
        elif ((self.get_alarm_para_startaddr() <= addr)
              and (self.get_alarm_para_endaddr() >= addr)):
            for key0 in self.alarm_para:
                for key1 in self.alarm_para[key0]:
                    for key2 in self.alarm_para[key0][key1]:
                        if (addr == self.alarm_para[key0][key1][key2].addr):
                            return self.alarm_para[key0][key1][key2]
        return False


    def init_data(self):
        for key in self.calibrate_para:
            self.calibrate_para[key].read_value = None
            self.calibrate_para[key].write_value = None
            self.calibrate_para[key].write_mode = WriteParameterMode.write_ram
            self.calibrate_para[key].read_ok_flag = None
            self.calibrate_para[key].write_ok_flag = None

class DebugCommand():
    def __init__(self):
        self.bool_echo = {
            '进入透传模式': None,     # None:主机没发命令， False：主机已发命令(等待从机应答)， True:从机已应答
            '退出透传模式': None
        }
        self.addr = {
            '下位机地址': None,
        }


'''
Parameter = DcboardParameter()
for key in Parameter.calibrate_para:
    if (20 == Parameter.calibrate_para[key].addr):
        print(key)
        print(Parameter.calibrate_para[key].writestatus)
        Parameter.calibrate_para[key].writestatus = CommandState.wait_response
        print(Parameter.calibrate_para[key].writestatus)
'''

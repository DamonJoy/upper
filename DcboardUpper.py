import sys
import  threading,time
from threading import Thread
from datetime import datetime
from time import strftime, localtime
from CanProtocol import *

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLCDNumber, QLabel, QDialog
from MainWindow import Ui_MainWindow
from ConfigDialog_Can import Ui_ConfigDialog_Can
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QObject, pyqtSignal, QThread

class CaliType(Enum):
    '''软件自定义, Mywindow 发送写KB值信号 给ThreadSendDcboardCommand时，给出此参数'''
    battend_volt = 0
    battend_chgcurr = 1
    battend_dsgcurr = 2
    loadend_volt = 3
    loadend_chgcurr = 4
    loadend_dsgcurr = 5

class VersionType(Enum):
    '''软件自定义，Mywindow 发送写版本信号 给ThreadSendDcboardCommand时,给出此参数；ThreadSendDcboardCommand 发送读版本结果信号 给Mywindow时，给出此参数'''
    software = 0
    hardware = 1
    pcb_sn = 2
    productname = 3
    module_sn = 4

class CommunicationState(Enum):
    '''软件自定义，ThreadCopyDeviceDataToBuff 发送通达信 对象掉线/上线信号 给Mywindow时，给出此参数'''
    offline = 0
    online = 1

class WidgetStringShow():
    '''控件根据整型值来显示字符串'''
    def __init__(self):
        self.widget = {
            'label_boardstate':
                {
                    '初始化':0,
                    '自检':1,
                    '待机':2,
                    '预上电':3,
                    '直通模式-直通' :4,
                    '直通模式-放电限流':5,
                    '直通模式-充电限流': 6,
                    '降压放电': 7,
                    '升压放电':8,
                    '降压充电':9,
                    '升压充电':10,
                    '禁充':11,
                    '禁放':12,
                    '关断':13,
                    '故障':14
                },
            #'alarm_level':
            #    {
            #        '无告警': 0,
            #        '一级告警': 1,
            #        '二级告警': 2,
            #    },
            'qlabel_bms_offline_alarm':
                {
                    'BMS离线一级告警': 1,
                    'BMS离线二级告警': 2,
                },
            'qlabel_mos_overtemp_alarm':
                {
                    'MOS过温一级告警': 1,
                    'MOS过温二级告警': 2,
                },
            'qlabel_loadend_overvolt_alarm':
                {
                    '负载端过压一级告警': 1,
                    '负载端过压二级告警': 2,
                },
            'qlabel_loadend_undervolt_alarm':
                {
                    '负载端欠压一级告警': 1,
                    '负载端欠压二级告警': 2,
                },
            'qlabel_loadend_chgovercurrent_alarm':
                {
                    '负载端充电过流一级告警': 1,
                    '负载端充电过流二级告警': 2,
                },
            'qlabel_loadend_dsgovercurrent_alarm':
                {
                    '负载端放电过流一级告警': 1,
                    '负载端放电过流二级告警': 2,
                },
            'qlabel_battend_overvolt_alarm':
                {
                    '电池端过压一级告警': 1,
                    '电池端过压二级告警': 2,
                },
            'qlabel_battend_undervolt_alarm':
                {
                    '电池端欠压一级告警': 1,
                    '电池端欠压二级告警': 2,
                },
            'qlabel_battend_chgovercurrent_alarm':
                {
                    '电池端充电过流一级告警': 1,
                    '电池端充电过流二级告警': 2,
                },
            'qlabel_battend_dsgovercurrent_alarm':
                {
                    '电池端放电过流一级告警': 1,
                    '电池端放电过流二级告警': 2,
                },
            'label_relay1state':
                {
                    '断开': 0,
                    '闭合': 1,
                    '故障': 2
                },
            'label_relay2state':
                {
                    '断开': 0,
                    '闭合': 1,
                    '故障': 2
                },
            'label_reversestate':
                {
                    '正常': 0,
                    '反接': 1
                },
            'label_controlcommand':
                {
                    '关断': 0,
                    '自动控制': 1,
                    '禁充': 2,
                    '禁放': 3,
                },
            'label_setworkmode':
                {
                    '铅酸锂电混用模式': 0,
                    '锂电优先模式': 1,
                    '锂电新旧混用模式': 2,
                    '铅酸优先模式': 3,
                    '远供升压模式': 4
                },
            'label_controlmainrelaycommand':
                {
                    '不控制': 0,
                    '强制断开': 1
                },
        }

class BoardState():
    def __init__(self):
        self.state = {
            '初始化':0,
            '自检':1,
            '待机':2,
            '预上电':3,
            '直通模式-直通' :4,
            '直通模式-放电限流':5,
            '直通模式-充电限流': 6,
            '降压放电': 7,
            '升压放电':8,
            '降压充电':9,
            '升压充电':10,
            '禁充':11,
            '禁放':12,
            '关断':13,
            '故障':14,
        }

class MyMainWindow(QMainWindow, Ui_MainWindow):
    write_version_signal = pyqtSignal(int , str)   # type, 版本字符串
    write_cali_signal = pyqtSignal(int,int, int)  # type, K, B值
    exit_signal = pyqtSignal()

    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)  # 初始化ui
        self.initwidget()
        self.widget_str_show = WidgetStringShow()
        self.connect_signal_slot()


    def closeEvent(self, event):
        g_can_device.closedevice()
        #self.exit_signal.emit()


    def initwidget(self):
        #self.lineedit_battend_cali_splvolt1.setValidator(QtGui.QIntValidator()) #设置只能输入int类型的数据

        self.lineedit_battend_cali_splvolt1.setValidator(QtGui.QDoubleValidator())
        self.lineedit_battend_cali_splvolt2.setValidator(QtGui.QDoubleValidator())
        self.lineedit_battend_cali_realvolt1.setValidator(QtGui.QDoubleValidator())
        self.lineedit_battend_cali_realvolt2.setValidator(QtGui.QDoubleValidator())

        self.lineedit_battend_cali_splchgcurr1.setValidator(QtGui.QDoubleValidator())  # 设置只能输入int类型的数据
        self.lineedit_battend_cali_splchgcurr2.setValidator(QtGui.QDoubleValidator())
        self.lineedit_battend_cali_realchgcurr1.setValidator(QtGui.QDoubleValidator())
        self.lineedit_battend_cali_realchgcurr2.setValidator(QtGui.QDoubleValidator())

        self.lineedit_battend_cali_spldsgcurr1.setValidator(QtGui.QDoubleValidator())  # 设置只能输入int类型的数据
        self.lineedit_battend_cali_spldsgcurr2.setValidator(QtGui.QDoubleValidator())
        self.lineedit_battend_cali_realdsgcurr1.setValidator(QtGui.QDoubleValidator())
        self.lineedit_battend_cali_realdsgcurr2.setValidator(QtGui.QDoubleValidator())

        self.lineedit_loadend_cali_splvolt1.setValidator(QtGui.QDoubleValidator())  # 设置只能输入int类型的数据
        self.lineedit_loadend_cali_splvolt2.setValidator(QtGui.QDoubleValidator())
        self.lineedit_loadend_cali_realvolt1.setValidator(QtGui.QDoubleValidator())
        self.lineedit_loadend_cali_realvolt2.setValidator(QtGui.QDoubleValidator())

        self.lineedit_loadend_cali_splchgcurr1.setValidator(QtGui.QDoubleValidator())  # 设置只能输入int类型的数据
        self.lineedit_loadend_cali_splchgcurr2.setValidator(QtGui.QDoubleValidator())
        self.lineedit_loadend_cali_realchgcurr1.setValidator(QtGui.QDoubleValidator())
        self.lineedit_loadend_cali_realchgcurr2.setValidator(QtGui.QDoubleValidator())

        self.lineedit_loadend_cali_spldsgcurr1.setValidator(QtGui.QDoubleValidator())  # 设置只能输入int类型的数据
        self.lineedit_loadend_cali_spldsgcurr2.setValidator(QtGui.QDoubleValidator())
        self.lineedit_loadend_cali_realdsgcurr1.setValidator(QtGui.QDoubleValidator())
        self.lineedit_loadend_cali_realdsgcurr2.setValidator(QtGui.QDoubleValidator())

        self.qlabel_bms_offline_alarm.hide()
        self.qlabel_mos_overtemp_alarm.hide()
        self.qlabel_loadend_overvolt_alarm.hide()
        self.qlabel_loadend_undervolt_alarm.hide()
        self.qlabel_loadend_chgovercurrent_alarm.hide()
        self.qlabel_loadend_dsgovercurrent_alarm.hide()
        self.qlabel_battend_overvolt_alarm.hide()
        self.qlabel_battend_undervolt_alarm.hide()
        self.qlabel_battend_chgovercurrent_alarm.hide()
        self.qlabel_battend_dsgovercurrent_alarm.hide()
        self.qlabel_canfail.hide()
        self.qlabel_dc_offline.hide()
        obj_list = self.findChildren(QtWidgets.QLCDNumber)
        for object in obj_list:
            object.display('')
        obj_list = self.findChildren(QtWidgets.QLineEdit)
        for object in obj_list:
            object.setText('')
        #self.label_boardstate.setText('999')
        self.label_boardstate.setText('')
        self.label_relay1state.setText('')
        self.label_relay2state.setText('')
        self.label_reversestate.setText('')
        self.label_controlcommand.setText('')
        self.label_setworkmode.setText('')
        self.label_controlmainrelaycommand.setText('')
        self.label_softwareversion.setText('')
        self.label_hardwareversion.setText('')
        self.label_productname.setText('')


    def connect_signal_slot(self):
        self.button_writepcbsn.clicked.connect(self.send_write_version_signal)
        self.button_writemodulesn.clicked.connect(self.send_write_version_signal)

        self.button_read_battend_cali_splvolt1.clicked.connect(self.rcv_button_read_cali_sample_value_signal)
        self.button_read_battend_cali_splvolt2.clicked.connect(self.rcv_button_read_cali_sample_value_signal)
        self.button_read_battend_cali_splchgcurr1.clicked.connect(self.rcv_button_read_cali_sample_value_signal)
        self.button_read_battend_cali_splchgcurr2.clicked.connect(self.rcv_button_read_cali_sample_value_signal)
        self.button_read_battend_cali_spldsgcurr1.clicked.connect(self.rcv_button_read_cali_sample_value_signal)
        self.button_read_battend_cali_spldsgcurr2.clicked.connect(self.rcv_button_read_cali_sample_value_signal)

        self.button_read_loadend_cali_splvolt1.clicked.connect(self.rcv_button_read_cali_sample_value_signal)
        self.button_read_loadend_cali_splvolt2.clicked.connect(self.rcv_button_read_cali_sample_value_signal)
        self.button_read_loadend_cali_splchgcurr1.clicked.connect(self.rcv_button_read_cali_sample_value_signal)
        self.button_read_loadend_cali_splchgcurr2.clicked.connect(self.rcv_button_read_cali_sample_value_signal)
        self.button_read_loadend_cali_spldsgcurr1.clicked.connect(self.rcv_button_read_cali_sample_value_signal)
        self.button_read_loadend_cali_spldsgcurr2.clicked.connect(self.rcv_button_read_cali_sample_value_signal)

        self.button_compute_battend_cali_volt_kb.clicked.connect(self.rcv_button_compute_cali_kb_signal)
        self.button_compute_battend_cali_chgcurr_kb.clicked.connect(self.rcv_button_compute_cali_kb_signal)
        self.button_compute_battend_cali_dsgcurr_kb.clicked.connect(self.rcv_button_compute_cali_kb_signal)

        self.button_compute_loadend_cali_volt_kb.clicked.connect(self.rcv_button_compute_cali_kb_signal)
        self.button_compute_loadend_cali_chgcurr_kb.clicked.connect(self.rcv_button_compute_cali_kb_signal)
        self.button_compute_loadend_cali_dsgcurr_kb.clicked.connect(self.rcv_button_compute_cali_kb_signal)

        self.button_write_battend_cali_volt_kb.clicked.connect(self.rcv_write_cali_kb_to_dcboard_signal)
        self.button_write_battend_cali_chgcurr_kb.clicked.connect(self.rcv_write_cali_kb_to_dcboard_signal)
        self.button_write_battend_cali_dsgcurr_kb.clicked.connect(self.rcv_write_cali_kb_to_dcboard_signal)

        self.button_write_loadend_cali_volt_kb.clicked.connect(self.rcv_write_cali_kb_to_dcboard_signal)
        self.button_write_loadend_cali_chgcurr_kb.clicked.connect(self.rcv_write_cali_kb_to_dcboard_signal)
        self.button_write_loadend_cali_dsgcurr_kb.clicked.connect(self.rcv_write_cali_kb_to_dcboard_signal)


    def rcv_write_command_result_signal(self, str):
        msg_box = QMessageBox(QMessageBox.Information, '提示', str)
        msg_box.exec_()


    def rcv_read_version_command_result_signal(self, type, flag, str):
        if (VersionType.pcb_sn.value == type):
            show_widget = self.lineedit_pcbsn
            hint = '读PCB序列号'
        elif (VersionType.module_sn.value == type):
            show_widget = self.lineedit_modulesn
            hint = '读模组序列号'
        else:
            return
        if (False == flag):
            msg_box = QMessageBox(QMessageBox.Information, '提示', hint + '失败!')
            msg_box.exec_()
            return
        show_widget.setText(str)


    def rcv_update_widget_value_signal(self, widget_dict):
        widget_key = '控件对象'
        value_key = '对象的值'
        if ((widget_key not in widget_dict.keys()) or (value_key not in widget_dict.keys())):
            return
        object = widget_dict[widget_key]
        value = widget_dict[value_key]
        if (isinstance(object, QtWidgets.QLabel)):
            if((object == self.label_softwareversion)
                or (object == self.label_hardwareversion)
                or (object == self.label_productname)):
                object.setText(value)
                return

            name = object.objectName()
            if(name not in self.widget_str_show.widget.keys()):
                return
            show_str = ''
            for k, v in self.widget_str_show.widget[name].items():
                if (v == value):
                    show_str = k
                    break
            if((object == self.qlabel_bms_offline_alarm)
                or (object == self.qlabel_mos_overtemp_alarm)
                or (object == self.qlabel_loadend_overvolt_alarm)
                or (object == self.qlabel_loadend_undervolt_alarm)
                or (object == self.qlabel_loadend_chgovercurrent_alarm)
                or (object == self.qlabel_loadend_dsgovercurrent_alarm)
                or (object == self.qlabel_battend_overvolt_alarm)
                or (object == self.qlabel_battend_undervolt_alarm)
                or (object == self.qlabel_battend_chgovercurrent_alarm)
                or (object == self.qlabel_battend_dsgovercurrent_alarm)):
                if(0 == value):
                    object.hide()
                else:
                    object.setText(show_str)
                    object.show()
                return
            object.setText(show_str)
        elif (isinstance(object, QtWidgets.QLCDNumber)):
            object.display(value)
        elif (isinstance(object, QtWidgets.QLineEdit)):
            object.setText(value)
        else:
            pass


    def rcv_button_read_cali_sample_value_signal(self):
        battend_volt = g_common_data.data['batteryend_volt'].received_value
        battend_volt = round(battend_volt, 1)  # 保留一位小数
        battend_curr = g_common_data.data['batteryend_current'].received_value
        battend_curr = round(battend_curr, 1)

        loadend_volt = g_common_data.data['loadend_volt'].received_value
        loadend_volt = round(loadend_volt, 1)
        loadend_curr = g_common_data.data['loadend_current'].received_value
        loadend_curr = round(loadend_curr, 1)

        sender = self.sender()
        show_widget = None
        show_str = ''
        if (self.button_read_battend_cali_splvolt1 == sender):
            show_str = str(battend_volt)
            show_widget = self.lineedit_battend_cali_splvolt1
        if (self.button_read_battend_cali_splvolt2 == sender):
            show_str = str(battend_volt)
            show_widget = self.lineedit_battend_cali_splvolt2
        elif (self.button_read_battend_cali_splchgcurr1 == sender):
            show_str = str(battend_curr)
            show_widget = self.lineedit_battend_cali_splchgcurr1
        elif (self.button_read_battend_cali_splchgcurr2 == sender):
            show_str = str(battend_curr)
            show_widget = self.lineedit_battend_cali_splchgcurr2
        elif (self.button_read_battend_cali_spldsgcurr1 == sender):
            show_str = str(battend_curr)
            show_widget = self.lineedit_battend_cali_spldsgcurr1
        elif (self.button_read_battend_cali_spldsgcurr2 == sender):
            show_str = str(battend_curr)
            show_widget = self.lineedit_battend_cali_spldsgcurr2

        if (self.button_read_loadend_cali_splvolt1 == sender):
            show_str = str(loadend_volt)
            show_widget = self.lineedit_loadend_cali_splvolt1
        if (self.button_read_loadend_cali_splvolt2 == sender):
            show_str = str(loadend_volt)
            show_widget = self.lineedit_loadend_cali_splvolt2
        elif (self.button_read_loadend_cali_splchgcurr1 == sender):
            show_str = str(loadend_curr)
            show_widget = self.lineedit_loadend_cali_splchgcurr1
        elif (self.button_read_loadend_cali_splchgcurr2 == sender):
            show_str = str(battend_curr)
            show_widget = self.lineedit_loadend_cali_splchgcurr2
        elif (self.button_read_loadend_cali_spldsgcurr1 == sender):
            show_str = str(battend_curr)
            show_widget = self.lineedit_loadend_cali_spldsgcurr1
        elif (self.button_read_loadend_cali_spldsgcurr2 == sender):
            show_str = str(battend_curr)
            show_widget = self.lineedit_loadend_cali_spldsgcurr2

        if(None != show_widget):
            show_widget.setText(show_str)


    def rcv_button_compute_cali_kb_signal(self):
        sample1 = None
        real1 = None
        sample2 = None
        real2 = None
        sender = self.sender()
        if(self.button_compute_battend_cali_volt_kb == sender):
            text_sample1_widget = self.lineedit_battend_cali_splvolt1
            text_sample2_widget = self.lineedit_battend_cali_splvolt2
            text_real1_widget = self.lineedit_battend_cali_realvolt1
            text_real2_widget = self.lineedit_battend_cali_realvolt2
            show_k_widget = self.lineedit_battend_cali_volt_k
            show_b_widget = self.lineedit_battend_cali_volt_b
        elif (self.button_compute_battend_cali_chgcurr_kb == sender):
            text_sample1_widget = self.lineedit_battend_cali_splchgcurr1
            text_sample2_widget = self.lineedit_battend_cali_splchgcurr2
            text_real1_widget = self.lineedit_battend_cali_realchgcurr1
            text_real2_widget = self.lineedit_battend_cali_realchgcurr2
            show_k_widget = self.lineedit_battend_cali_chgcurr_k
            show_b_widget = self.lineedit_battend_cali_chgcurr_b
        elif (self.button_compute_battend_cali_dsgcurr_kb == sender):
            text_sample1_widget = self.lineedit_battend_cali_spldsgcurr1
            text_sample2_widget = self.lineedit_battend_cali_spldsgcurr2
            text_real1_widget = self.lineedit_battend_cali_realdsgcurr1
            text_real2_widget = self.lineedit_battend_cali_realdsgcurr2
            show_k_widget = self.lineedit_battend_cali_dsgcurr_k
            show_b_widget = self.lineedit_battend_cali_dsgcurr_b
        elif (self.button_compute_loadend_cali_volt_kb == sender):
            text_sample1_widget = self.lineedit_loadend_cali_splvolt1
            text_sample2_widget = self.lineedit_loadend_cali_splvolt2
            text_real1_widget = self.lineedit_loadend_cali_realvolt1
            text_real2_widget = self.lineedit_loadend_cali_realvolt2
            show_k_widget = self.lineedit_loadend_cali_volt_k
            show_b_widget = self.lineedit_loadend_cali_volt_b
        elif (self.button_compute_loadend_cali_chgcurr_kb == sender):
            text_sample1_widget = self.lineedit_loadend_cali_splchgcurr1
            text_sample2_widget = self.lineedit_loadend_cali_splchgcurr2
            text_real1_widget = self.lineedit_loadend_cali_realchgcurr1
            text_real2_widget = self.lineedit_loadend_cali_realchgcurr2
            show_k_widget = self.lineedit_loadend_cali_chgcurr_k
            show_b_widget = self.lineedit_loadend_cali_chgcurr_b
        elif (self.button_compute_loadend_cali_dsgcurr_kb == sender):
            text_sample1_widget = self.lineedit_loadend_cali_spldsgcurr1
            text_sample2_widget = self.lineedit_loadend_cali_spldsgcurr2
            text_real1_widget = self.lineedit_loadend_cali_realdsgcurr1
            text_real2_widget = self.lineedit_loadend_cali_realdsgcurr2
            show_k_widget = self.lineedit_loadend_cali_dsgcurr_k
            show_b_widget = self.lineedit_loadend_cali_dsgcurr_b
        else:
            return

        text = text_sample1_widget.text()
        text = text.strip()
        if ('' != text):
            sample1 = float(text)

        text = text_sample2_widget.text()
        text = text.strip()
        if ('' != text):
            sample2 = float(text)

        text = text_real1_widget.text()
        text = text.strip()
        if ('' != text):
            real1 = float(text)

        text = text_real2_widget.text()
        text = text.strip()
        if ('' != text):
            real2 = float(text)

        if((None == sample1) or (None == sample2) or (None == real1) or (None == real2)):
            msg_box = QMessageBox(QMessageBox.Information, '提示', '请输入采样值和真实值!')
            msg_box.exec_()
            return

        if(sample2 == sample1):
            msg_box = QMessageBox(QMessageBox.Information, '提示', '两次采样值不能相同!')
            msg_box.exec_()
            return
        cali_k = (real2 - real1) / (sample2 - sample1)
        cali_b = real1 - cali_k * sample1
        cali_k = int(cali_k * 1000)
        cali_b = int(cali_b * 10)
        str_k = str(cali_k)
        str_b = str(cali_b)

        show_k_widget.setText(str_k)
        show_b_widget.setText(str_b)


    def rcv_write_cali_kb_to_dcboard_signal(self):
        sender = self.sender()
        if (self.button_write_battend_cali_volt_kb == sender):
            text_cali_k_widget = self.lineedit_battend_cali_volt_k
            text_cali_b_widget = self.lineedit_battend_cali_volt_b
            cali_type =  CaliType.battend_volt.value
        elif (self.button_write_battend_cali_chgcurr_kb == sender):
            text_cali_k_widget = self.lineedit_battend_cali_chgcurr_k
            text_cali_b_widget = self.lineedit_battend_cali_chgcurr_b
            cali_type = CaliType.battend_chgcurr.value
        elif (self.button_write_battend_cali_dsgcurr_kb == sender):
            text_cali_k_widget = self.lineedit_battend_cali_dsgcurr_k
            text_cali_b_widget = self.lineedit_battend_cali_dsgcurr_b
            cali_type = CaliType.battend_dsgcurr.value
        elif (self.button_write_loadend_cali_volt_kb == sender):
            text_cali_k_widget = self.lineedit_loadend_cali_volt_k
            text_cali_b_widget = self.lineedit_loadend_cali_volt_b
            cali_type = CaliType.loadend_volt.value
        elif (self.button_write_loadend_cali_chgcurr_kb == sender):
            text_cali_k_widget = self.lineedit_loadend_cali_chgcurr_k
            text_cali_b_widget = self.lineedit_loadend_cali_chgcurr_b
            cali_type = CaliType.loadend_chgcurr.value
        elif (self.button_write_loadend_cali_dsgcurr_kb == sender):
            text_cali_k_widget = self.lineedit_loadend_cali_dsgcurr_k
            text_cali_b_widget = self.lineedit_loadend_cali_dsgcurr_b
            cali_type = CaliType.loadend_dsgcurr.value
        else:
            return

        if(('' == text_cali_k_widget.text()) or ('' == text_cali_b_widget.text())):
            msg_box = QMessageBox(QMessageBox.Information, '提示', 'KB值不能为空!')
            msg_box.exec_()
            return

        cali_k = int(text_cali_k_widget.text())
        cali_b = int(text_cali_b_widget.text())
        if(cali_k < 0):
            cali_k = 32768 + (32768 + cali_k)
        if (cali_b < 0):
            cali_b = 32768 + (32768 + cali_b)
        self.write_cali_signal.emit(cali_type, cali_k, cali_b)


    def rcv_dcboard_online_offline_signal(self, state):
        if(CommunicationState.offline.value == state):
            self.initwidget()
            g_common_data.init_data()
            g_version_data.init_data()
            g_public_data.init_data()
            g_parameter.init_data()
            self.qlabel_dc_offline.show()
        elif (CommunicationState.online.value == state):
            self.qlabel_dc_offline.hide()
        else:
            pass


    def rcv_can_device_online_offline_signal(self, state):
        if(CommunicationState.offline.value == state):
            self.initwidget()
            self.qlabel_canfail.show()
        elif (CommunicationState.online.value == state):
            self.qlabel_canfail.hide()
        else:
            pass


    def send_write_version_signal(self):
        sender = self.sender()
        if (self.button_writepcbsn == sender):
            object_widget = self.lineedit_pcbsn
            type = VersionType.pcb_sn.value
        elif(self.button_writemodulesn == sender):
            object_widget = self.lineedit_modulesn
            type = VersionType.module_sn.value
        else:
            return

        str = object_widget.text()
        if('' == str):
            msg_box = QMessageBox(QMessageBox.Information, '提示', '请输入内容!')
            msg_box.exec_()
            return
        #str = str.strip()     # 去除两边空格
        char_len = len(str)
        max_len = g_version_data.package_len * 6
        version_str = ''
        if (max_len < char_len):
            for i in range(max_len):
                version_str = version_str + str[i]
        else:
            version_str = str
        self.write_version_signal.emit(type, version_str)

class ConfigCanDialog(QDialog, Ui_ConfigDialog_Can):
    can_device_online_offline_signal = pyqtSignal(int)  # 0:掉线， 1:上线
    def __init__(self):
        super(ConfigCanDialog, self).__init__()
        self.setupUi(self)  # 初始化ui
        self.connect_signal_slot()
        self.button_closecan.setEnabled(False)


    def connect_signal_slot(self):
        self.button_opencan.clicked.connect(self.rcv_open_can_signal)
        self.button_closecan.clicked.connect(self.rcv_close_can_signal)

    def rcv_open_can_signal(self):
        global g_can_device_offline_flag
        ret = g_can_device.init()
        if (True == ret):
            g_can_device_offline_flag = False
            self.labe_canstate.setText('已打开')
            self.can_device_online_offline_signal.emit(CommunicationState.online.value)  # CAN上线
            self.button_closecan.setEnabled(True)
            self.button_opencan.setEnabled(False)
            self.close()


    def rcv_close_can_signal(self):
        global g_can_device_offline_flag
        ret = g_can_device.closedevice()
        if (True == ret):
            g_can_device_offline_flag = True
            self.labe_canstate.setText('已关闭')
            self.can_device_online_offline_signal.emit(CommunicationState.offline.value)  # CAN下线
            self.button_closecan.setEnabled(False)
            self.button_opencan.setEnabled(True)


class ThreadSendDcboardCommand(QThread):
    write_result_signal = pyqtSignal(str)  # 提示字符
    read_version_result_signal = pyqtSignal(int, bool, str) # version类型， 读成功/失败, 读的字符串

    def __init__(self):
        super().__init__()
        pass


    def run(self):
        type = 0
        last_time_ms = 0
        while True:
            if (False == g_can_device_offline_flag):
                curr_time_ms = int(round(time.time() * 1000))
                if ((curr_time_ms - last_time_ms) >= 500):
                    if(True != g_version_data.data['software'].read_ok_flag):
                        g_version_data.data['software'].read_ok_flag = False
                        g_protocol.send_read_version_command(g_can_device, g_channel, 'software')
                    if (True != g_version_data.data['hardware'].read_ok_flag):
                        g_version_data.data['hardware'].read_ok_flag = False
                        g_protocol.send_read_version_command(g_can_device, g_channel, 'hardware')
                    if (True != g_version_data.data['productname'].read_ok_flag):
                        g_version_data.data['productname'].read_ok_flag = False
                        g_protocol.send_read_version_command(g_can_device, g_channel, 'productname')
                    data_num = 1
                    for addr in range(3, 17):
                        g_protocol.send_read_public_data_command(g_can_device, g_channel, type, addr, data_num)
                    last_time_ms = int(round(time.time() * 1000))

            self.msleep(5)


    def rcv_read_version_signal(self):
        sender = main_window.sender()
        if(main_window.button_readpcbsn == sender):
            type_key = 'pcb_sn'
            type = VersionType.pcb_sn.value
        elif(main_window.button_readmodulesn == sender):
            type_key = 'module_sn'
            type = VersionType.module_sn.value
        else:
            return
        if(type_key not in g_version_data.data.keys()):
            return

        g_version_data.data[type_key].read_ok_flag = False
        last_time_ms = 0
        wait_time_ms = 0
        start_time = int(round(time.time() * 1000))
        while (wait_time_ms < 2000):
            if (True == g_version_data.data[type_key].read_ok_flag):
                break
            curr_time_ms = int(round(time.time() * 1000))
            if ((curr_time_ms - last_time_ms) > 200):
                g_protocol.send_read_version_command(g_can_device, g_channel, type_key)
                last_time_ms = int(round(time.time() * 1000))
                self.msleep(5)
            curr_time_ms = int(round(time.time() * 1000))
            wait_time_ms = curr_time_ms - start_time

        version_str = ''
        flag = False
        if (True == g_version_data.data[type_key].read_ok_flag):
            version_str = g_version_data.data[type_key].version_str
            flag = True
        g_version_data.data[type_key].read_ok_flag = None
        self.read_version_result_signal.emit(type, flag, version_str)


    def rcv_write_version_signal(self, type, version_str):
        if (VersionType.pcb_sn.value == type):
            para_startaddr = 40         # pcb_sn参数起始地址为 40, 每个地址存2个字节
            result_str = '写PCB序列号'
        elif (VersionType.module_sn.value == type):
            para_startaddr = 52         # module_sn参数起始地址为 52, 每个地址存2个字节
            result_str = '写模组序列号'
        else:
            return

        str_len = len(version_str)
        max_len = g_version_data.package_len * 6
        if(str_len > max_len):
           str_len = max_len
        ascii_bytes = []
        for i in range(str_len):
            ascii_bytes.append(ord(version_str[i]))  # 计算并保存各字符的ascii码
        ascii_len = len(ascii_bytes)
        if(ascii_len < max_len):
            for i in range(max_len - ascii_len):
                ascii_bytes.append(0)       # ascii码数量不足max_len，则不足的部分全部为0
        write_cnt = max_len // 2      # 每次写2Bytes

        for i in range(write_cnt):
            para_addr = para_startaddr + i
            para = g_parameter.get_parameter(para_addr)
            if (False == para):
                self.write_result_signal.emit('参数未定义!')
                return
            para.write_value = (ascii_bytes[i * 2] << 8) | ascii_bytes[i * 2 + 1]
            para.write_mode = WriteParameterMode.write_ram_eeprom
            para.write_ok_flag = False
            last_time_ms = 0
            wait_time_ms = 0
            start_time = int(round(time.time() * 1000))
            while (wait_time_ms < 2000):
                if (True == para.write_ok_flag):
                    break
                curr_time_ms = int(round(time.time() * 1000))
                if ((curr_time_ms - last_time_ms) > 200):
                    g_protocol.send_write_parameter_command(g_can_device, g_channel, mode=para.write_mode,
                                                               para_addr=para.addr, para_value=para.write_value)
                    last_time_ms = int(round(time.time() * 1000))
                    self.msleep(5)
                curr_time_ms = int(round(time.time() * 1000))
                wait_time_ms = curr_time_ms - start_time

            if (True != para.write_ok_flag):
                self.write_result_signal.emit(result_str + '失败!')
                para.write_ok_flag = None
                return
            para.write_ok_flag = None
        self.write_result_signal.emit(result_str + '成功!')


    def rcv_write_cali_signal(self, type, k_value, b_value):
        if(CaliType.battend_volt.value == type):
            k_addr = 15
            b_addr = 16
        elif (CaliType.battend_chgcurr.value == type):
            k_addr = 19
            b_addr = 20
        elif (CaliType.battend_dsgcurr.value == type):
            k_addr = 21
            b_addr = 22
        elif (CaliType.loadend_volt.value == type):
            k_addr = 17
            b_addr = 18
        elif (CaliType.loadend_chgcurr.value == type):
            k_addr = 23
            b_addr = 24
        elif (CaliType.loadend_dsgcurr.value == type):
            k_addr = 25
            b_addr = 26
        else:
            self.write_result_signal.emit('参数地址未定义!')
            return

        para_k = g_parameter.get_parameter(k_addr)
        para_b = g_parameter.get_parameter(b_addr)
        if ((False == para_k) or (False == para_b)):
            self.write_result_signal.emit('参数未定义!')
            return

        para_k.write_value = k_value
        para_b.write_value = b_value
        para_k.write_mode = WriteParameterMode.write_ram_eeprom
        para_b.write_mode = WriteParameterMode.write_ram_eeprom
        para_k.write_ok_flag = False
        para_b.write_ok_flag = False
        last_time_ms = 0
        wait_time_ms = 0
        start_time = int(round(time.time() * 1000))
        while (wait_time_ms < 2000):
            if ((True == para_k.write_ok_flag) and (True == para_b.write_ok_flag)):
                break
            curr_time_ms = int(round(time.time() * 1000))
            if ((curr_time_ms - last_time_ms) > 200):
                g_protocol.send_write_parameter_command(g_can_device, g_channel, mode=para_k.write_mode,
                                                           para_addr=para_k.addr, para_value=para_k.write_value)
                g_protocol.send_write_parameter_command(g_can_device, g_channel, mode=para_b.write_mode,
                                                           para_addr=para_b.addr, para_value=para_b.write_value)
                last_time_ms = int(round(time.time() * 1000))
                self.msleep(5)
            curr_time_ms = int(round(time.time() * 1000))
            wait_time_ms = curr_time_ms - start_time

        if ((True == para_k.write_ok_flag) and (True == para_b.write_ok_flag)):
            self.write_result_signal.emit('写KB值成功!')
        else:
            self.write_result_signal.emit('写KB值失败!')
        para_k.write_ok_flag = None
        para_b.write_ok_flag = None


    def rcv_write_transparent_mode_signal(self):
        addr = main_window.lineedit_target_canaddr.text()
        addr = addr.strip()  # 去除两边空格
        try:
            valid_flag = True
            addr = int(addr, 16)
            if (addr > 0xFF):
                valid_flag = False
        except ValueError:
            valid_flag = False
        if(False == valid_flag):
            msg_box = QMessageBox(QMessageBox.Information, '提示', '请输入正确的目标地址(十六进制)')
            msg_box.exec_()
            return
        g_debug_command.addr['下位机地址'] = addr

        sender = self.sender()
        type_key = ''
        if (main_window.button_enter_transparent == sender):
            mode = 0x01
            type_key = '进入透传模式'
        elif (main_window.button_exit_transparent == sender):
            mode = 0x00
            type_key = '退出透传模式'
        else:
            return
        if(type_key not in g_debug_command.bool_echo.keys()):
            return

        g_debug_command.bool_echo[type_key] = False
        last_time_ms = 0
        wait_time_ms = 0
        start_time = int(round(time.time() * 1000))
        while(wait_time_ms < 2000):
            if (True == g_debug_command.bool_echo[type_key]):
                break
            curr_time_ms = int(round(time.time() * 1000))
            if((curr_time_ms - last_time_ms) > 200):
                g_protocol.send_write_transparent_mode_command(g_can_device, g_channel, target_canaddr=addr, mode=mode)
                last_time_ms = int(round(time.time() * 1000))
                self.msleep(5)
            curr_time_ms = int(round(time.time() * 1000))
            wait_time_ms = curr_time_ms - start_time

        result_str = type_key + '失败!'
        if(True == g_debug_command.bool_echo[type_key]):
            result_str = type_key + '成功!'
        g_debug_command.bool_echo[type_key] = None
        self.write_result_signal.emit(result_str)


class ThreadCopyDeviceDataToBuff(QThread):
    dcboard_online_offline_signal = pyqtSignal(int)  # 0:掉线， 1:上线
    can_device_online_offline_signal = pyqtSignal(int)  # 0:掉线， 1:上线

    def __init__(self):
        super().__init__()


    def rcv_exit_signal(self):
        g_can_device.closedevice()


    def run(self):
        global g_dcboard_offline_cnt
        global g_dcboard_offline_flag
        dcboard_offline_delay_ms = 1500
        dcboard_offline_last_time_ms = 0

        while True:
            if(g_dcboard_offline_cnt < (dcboard_offline_delay_ms // 100)):
                curr_time_ms = int(round(time.time() * 1000))
                if ((curr_time_ms - dcboard_offline_last_time_ms) > 100):
                    g_dcboard_offline_cnt = g_dcboard_offline_cnt + 1
                    dcboard_offline_last_time_ms = int(round(time.time() * 1000))

            if(False == g_can_device_offline_flag):
                if((dcboard_offline_delay_ms // 100) <= g_dcboard_offline_cnt) and (False == g_dcboard_offline_flag):
                    g_dcboard_offline_flag = True
                    self.dcboard_online_offline_signal.emit(CommunicationState.offline.value)    # DC掉线
                elif((dcboard_offline_delay_ms // 100) > g_dcboard_offline_cnt) and (True == g_dcboard_offline_flag):
                    g_dcboard_offline_flag = False
                    self.dcboard_online_offline_signal.emit(CommunicationState.online.value)     # DC上线

            if(False == g_can_device_offline_flag):
                g_can_device.copy_device_data_to_rcv_buff(g_channel)
            self.msleep(g_can_device.rcv_interval_ms)

class ThreadSendBuffDataToDevice(QThread):
    def __init__(self):
        super().__init__()


    def run(self):
        while True:
            cnt = len(g_can_device.send_messagelist)
            for i in range(cnt):
                message = g_can_device.send_messagelist[0]
                g_can_device.sendmessage(g_channel, message)
                del g_can_device.send_messagelist[0]
                self.msleep(g_can_device.send_interval_ms)
            self.msleep(5)

class ThreadProcessData(QThread):
    update_widget_value_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()


    def __update_common_data_value(self, data_key, value):
        if (data_key not in g_common_data.data.keys()):
            return
        if (value == g_common_data.data[data_key].received_value):
            return
        g_common_data.data[data_key].received_value = value
        temp_dict = {'控件对象': g_common_data.data[data_key].widget, '对象的值': value}
        self.update_widget_value_signal.emit(temp_dict)


    def __analyze_dcboard_canframe0x300(self, databyte):
        data_value = (databyte[0] >> 0) & 0x3F  # bit0~bit5
        self.__update_common_data_value('boardstate', data_value)

        data_value = (databyte[0] >> 6) & 0x03  # bit6~bit7
        self.__update_common_data_value('alarmlevel', data_value)

        data_value = (databyte[1] >> 0) & 0x03  # bit0~bit1
        self.__update_common_data_value('relayk1state', data_value)

        data_value = (databyte[1] >> 2) & 0x03  # bit2~bit3
        self.__update_common_data_value('relayk2state', data_value)

        data_value = (databyte[1] >> 4) & 0x01  # bit4
        self.__update_common_data_value('reverseflag', data_value)

        data_value = (databyte[2] >> 4) & 0x03  # bit4~bit5
        self.__update_common_data_value('alarm_bms_offline', data_value)

        data_value = (databyte[2] >> 6) & 0x03  # bit6~bit7
        self.__update_common_data_value('alarm_mos_overtemp', data_value)

        data_value = (databyte[3] >> 0) & 0x03  # bit0~bit1
        self.__update_common_data_value('alarm_loadend_overvolt', data_value)

        data_value = (databyte[3] >> 2) & 0x03  # bit2~bit3
        self.__update_common_data_value('alarm_loadend_undervolt', data_value)

        data_value = (databyte[3] >> 4) & 0x03  # bit4~bit5
        self.__update_common_data_value('alarm_batteryend_overvolt', data_value)

        data_value = (databyte[3] >> 6) & 0x03  # bit6~bit7
        self.__update_common_data_value('alarm_batteryend_undervolt', data_value)

        data_value = (databyte[4] >> 0) & 0x03  # bit0~bit1
        self.__update_common_data_value('alarm_loadend_overchargecurrent', data_value)

        data_value = (databyte[4] >> 2) & 0x03  # bit2~bit3
        self.__update_common_data_value('alarm_loadend_overdischargecurrent', data_value)

        data_value = (databyte[4] >> 4) & 0x03  # bit4~bit5
        self.__update_common_data_value('alarm_batteryend_overchargecurrent', data_value)

        data_value = (databyte[4] >> 6) & 0x03  # bit6~bit7
        self.__update_common_data_value('alarm_batteryend_overdischargecurrent', data_value)

        data_value = databyte[5] - 40  # 原数据单位1'C/bit, 偏移量: -40'C
        self.__update_common_data_value('pcbtemp', data_value)

        data_value = databyte[6] - 40
        self.__update_common_data_value('mostemp1', data_value)

        data_value = databyte[7] - 40
        self.__update_common_data_value('mostemp2', data_value)


    def __analyze_dcboard_canframe0x301(self, databyte):
        # 原数据单位:0.1V/bit, 偏移量:0
        data_value = (((databyte[0] << 8) | (databyte[1])) / 10)
        self.__update_common_data_value('loadend_volt', data_value)

        data_value = (((databyte[4] << 8) | (databyte[5])) / 10)
        self.__update_common_data_value('batteryend_volt', data_value)

        # 原数据单位:0.1A/bit, 偏移量:-1600A, 放电电流为正
        data_value = (((databyte[2] << 8) | (databyte[3])) / 10 - 1600)
        self.__update_common_data_value('loadend_current', data_value)

        data_value = (((databyte[6] << 8) | (databyte[7])) / 10 - 1600)
        self.__update_common_data_value('batteryend_current', data_value)


    def __analyze_dcboard_read_version_echo(self, databyte):
        package_num = databyte[0]
        version_type = databyte[1]
        if(package_num <= 0) or (package_num > 0xF):
            return
        if(0x01 == version_type):
            data_key = 'software'
        elif(0x02 == version_type):
            data_key = 'hardware'
        elif(0x03 == version_type):
            data_key = 'pcb_sn'
        elif(0x04 == version_type):
            data_key = 'productname'
        elif(0x05 == version_type):
            data_key = 'module_sn'
        else:
            return

        for packge_bytes in g_version_data.data[data_key].package_list:
            if(package_num == packge_bytes[0]):
                return  # 此包已接收过，则直接丢弃此包

        g_version_data.data[data_key].package_list.append(databyte) # 保存此包
        if(len(g_version_data.data[data_key].package_list) < g_version_data.package_len):
            return     # 还有包没收到

        # 全部包已接收到
        sorted_ascii_bytes = []
        for i in range(g_version_data.package_len * 6):
            sorted_ascii_bytes.append(0)    # 用来保存按序排好的ASCII码
        for packge_bytes in g_version_data.data[data_key].package_list:
            package_num = packge_bytes[0]   # byte0为包序号
            for i in range(2, 8):
                byte_idx = 6 * package_num - (7 - i) - 1
                sorted_ascii_bytes[byte_idx] = packge_bytes[i]
        g_version_data.data[data_key].package_list.clear()

        version_str = ''
        for i in range(len(sorted_ascii_bytes)):
            ascii_code = sorted_ascii_bytes[i]
            if (0x00 == ascii_code):
                break
            version_str = version_str + chr(ascii_code)
        g_version_data.data[data_key].version_str = version_str
        if (False == g_version_data.data[data_key].read_ok_flag):
            g_version_data.data[data_key].read_ok_flag = True   # 有任务在等待读结果，设置标志
        temp_dict = {'控件对象': g_version_data.data[data_key].widget, '对象的值': version_str}
        self.update_widget_value_signal.emit(temp_dict)


    def __analyze_dcboard_read_publicdata_echo(self, databyte):
        data_type = databyte[1]
        data_addr = (databyte[2] << 8) | databyte[3]
        data_value = (databyte[4] << 8) | databyte[5]
        publicdata = g_public_data.get_public_data(type=data_type, addr=data_addr)
        if(False == publicdata):
            return
        if (False == publicdata.read_ok_flag):
            publicdata.read_ok_flag = True

        if((data_addr >= 6) and (data_addr <= 16)):
            data_value = data_value / 10
            data_value = round(data_value,1)  # 取1位小数

        if(data_value != publicdata.read_value):
            publicdata.read_value = data_value
            temp_dict = {'控件对象': publicdata.widget, '对象的值': data_value}
            self.update_widget_value_signal.emit(temp_dict)

    def __analyze_dcboard_write_para_echo(self, databyte):
        if (0x01 != databyte[0]):
            return  # 口令对不上
        para_addr = (databyte[1] << 8) | databyte[2]
        para_value = (databyte[3] << 8) | databyte[4]
        write_mode = databyte[5]
        para = g_parameter.get_parameter(para_addr)
        if (False == para):
            return
        if ((para_value == para.write_value) and (write_mode == para.write_mode.value) and (False == para.write_ok_flag)):
            para.write_ok_flag = True
            print(para.addr)


    def __analyze_dcboard_read_para_echo(self, databyte):
        para1_addr = (databyte[0] << 8) | databyte[1]
        para1_readvalue = (databyte[2] << 8) | databyte[3]
        para2_addr = (databyte[4] << 8) | databyte[5]
        para2_readvalue = (databyte[6] << 8) | databyte[7]
        para_list = [{'addr': para1_addr, 'readvalue': para1_readvalue},
                     {'addr': para2_addr, 'readvalue': para2_readvalue}]
        for temp_para in para_list:
            para = g_parameter.get_parameter(temp_para['addr'])
            if (False == para):
                break
            if (False == para.read_ok_flag):
                para.read_ok_flag = True
                para.read_value = temp_para['readvalue']


    def temp_test(self):
        pass

    def run(self):
        global g_dcboard_offline_cnt
        rcv_cnt = 0
        rcv_cnt1 = 0
        while True:
            for i in range(len(g_can_device.rcv_messagelist)):
                type = g_can_device.rcv_messagelist[0]['type']
                id = g_can_device.rcv_messagelist[0]['id']
                databyte = g_can_device.rcv_messagelist[0]['databyte']
                if(CanAddress.dcboard.value == (id & 0xFF)):
                    g_dcboard_offline_cnt = 0

                if (0x300 == id):
                    self.__analyze_dcboard_canframe0x300(databyte)
                    #rcv_cnt = rcv_cnt + 1
                    #print('300: %s' % rcv_cnt)
                elif (0x301 == id):
                    self.__analyze_dcboard_canframe0x301(databyte)
                elif ((0x19F40000 | (CanAddress.pc.value << 8) | CanAddress.dcboard.value) == id):
                    self.__analyze_dcboard_read_version_echo(databyte)  # Dcboard响应PC的读版本命令
                elif ((0x19F10000 | (CanAddress.pc.value << 8) | CanAddress.dcboard.value) == id):
                    self.__analyze_dcboard_write_para_echo(databyte)  # Dcboard响应PC的写参数命令
                    #rcv_cnt1 = rcv_cnt1 + 1
                    #print('19F1: %s' % rcv_cnt1)
                elif ((0x19F00000 | (CanAddress.pc.value << 8) | CanAddress.dcboard.value) == id):
                    self.__analyze_dcboard_read_para_echo(databyte)  # Dcboard响应PC的读参数命令
                elif ((0x19F20000 | (CanAddress.pc.value << 8) | CanAddress.dcboard.value) == id):
                    self.__analyze_dcboard_read_publicdata_echo(databyte)  # Dcboard响应PC的读公共数据命令
                elif(None != g_debug_command.addr['下位机地址']):
                    if((0x18FF0000 | (0xFF << 8) | g_debug_command.addr['下位机地址']) == id):
                        if((0xF8 == databyte[0]) and (0x01 == databyte[1])):
                            for key in g_debug_command.bool_echo:
                                if(False == g_debug_command.bool_echo[key]):
                                    g_debug_command.bool_echo[key] = True

                del g_can_device.rcv_messagelist[0]
            self.msleep(5)


def BindDataAndWidget():
    g_common_data.data['boardstate'].widget = main_window.label_boardstate
    g_common_data.data['alarmlevel'].widget = main_window.qlcd_alarmlevel
    g_common_data.data['relayk1state'].widget = main_window.label_relay1state
    g_common_data.data['relayk2state'].widget = main_window.label_relay2state
    g_common_data.data['reverseflag'].widget = main_window.label_reversestate
    g_common_data.data['alarm_bms_offline'].widget = main_window.qlabel_bms_offline_alarm
    g_common_data.data['alarm_mos_overtemp'].widget = main_window.qlabel_mos_overtemp_alarm
    g_common_data.data['alarm_loadend_overvolt'].widget = main_window.qlabel_loadend_overvolt_alarm
    g_common_data.data['alarm_loadend_undervolt'].widget = main_window.qlabel_loadend_undervolt_alarm
    g_common_data.data['alarm_batteryend_overvolt'].widget = main_window.qlabel_battend_overvolt_alarm
    g_common_data.data['alarm_batteryend_undervolt'].widget = main_window.qlabel_battend_undervolt_alarm
    g_common_data.data['alarm_loadend_overchargecurrent'].widget = main_window.qlabel_loadend_chgovercurrent_alarm
    g_common_data.data['alarm_loadend_overdischargecurrent'].widget = main_window.qlabel_loadend_dsgovercurrent_alarm
    g_common_data.data['alarm_batteryend_overchargecurrent'].widget = main_window.qlabel_battend_chgovercurrent_alarm
    g_common_data.data['alarm_batteryend_overdischargecurrent'].widget = main_window.qlabel_battend_dsgovercurrent_alarm
    g_common_data.data['pcbtemp'].widget = main_window.qlcd_pcbtemp
    g_common_data.data['mostemp1'].widget = main_window.qlcd_mostemp1
    g_common_data.data['mostemp2'].widget = main_window.qlcd_mostemp2
    g_common_data.data['loadend_volt'].widget = main_window.qlcd_loadend_volt
    g_common_data.data['loadend_current'].widget = main_window.qlcd_loadend_current
    g_common_data.data['batteryend_volt'].widget = main_window.qlcd_batteryend_volt
    g_common_data.data['batteryend_current'].widget = main_window.qlcd_batteryend_current

    g_version_data.data['software'].widget = main_window.label_softwareversion
    g_version_data.data['hardware'].widget = main_window.label_hardwareversion
    g_version_data.data['productname'].widget = main_window.label_productname

    g_public_data.receivedbmsdata['controlcommand'].widget = main_window.label_controlcommand
    g_public_data.receivedbmsdata['setworkmode'].widget = main_window.label_setworkmode
    g_public_data.receivedbmsdata['controlmainrelaycommand'].widget = main_window.label_controlmainrelaycommand
    g_public_data.receivedbmsdata['max_chargeablecurrent'].widget = main_window.qlcd_max_chargeablecurrent
    g_public_data.receivedbmsdata['max_chargeablevolt'].widget = main_window.qlcd_max_chargeablevolt
    g_public_data.receivedbmsdata['max_dischargeablecurrent'].widget = main_window.qlcd_max_dischargeablecurrent
    g_public_data.receivedbmsdata['min_dischargeablevolt'].widget = main_window.qlcd_min_dischargeablevolt
    g_public_data.receivedbmsdata['target_raiseddischargevolt'].widget = main_window.qlcd_target_raiseddischargevolt
    g_public_data.receivedbmsdata['leadacid_eodvolt'].widget = main_window.qlcd_leadacid_eodvolt
    g_public_data.receivedbmsdata['charger_maxchargevolt'].widget = main_window.qlcd_charger_maxchargevolt
    g_public_data.receivedbmsdata['min_raiseddischargevolt'].widget = main_window.qlcd_min_raiseddischargevolt
    g_public_data.receivedbmsdata['lithiumfirst_leadacidchargevolt'].widget = main_window.qlcd_lithiumfirst_leadacidchargevolt
    g_public_data.receivedbmsdata['leadacidfirst_reductiondischargevolt'].widget = main_window.qlcd_leadacidfirst_reductiondischargevolt
    g_public_data.receivedbmsdata['lithiumfirst_maxdischargeablevolt'].widget = main_window.qlcd_lithiumfirst_maxdischargeablevolt


def ConnectSignalSlot():
    main_window.write_version_signal.connect(thread_sendcommand.rcv_write_version_signal)
    main_window.write_cali_signal.connect(thread_sendcommand.rcv_write_cali_signal)
    main_window.button_readpcbsn.clicked.connect(thread_sendcommand.rcv_read_version_signal)
    main_window.button_readmodulesn.clicked.connect(thread_sendcommand.rcv_read_version_signal)
    main_window.button_enter_transparent.clicked.connect(thread_sendcommand.rcv_write_transparent_mode_signal)
    main_window.button_exit_transparent.clicked.connect(thread_sendcommand.rcv_write_transparent_mode_signal)
    main_window.exit_signal.connect(thread_read_candevice.rcv_exit_signal)

    thread_sendcommand.write_result_signal.connect(main_window.rcv_write_command_result_signal)
    thread_sendcommand.read_version_result_signal.connect(main_window.rcv_read_version_command_result_signal)

    thread_read_candevice.dcboard_online_offline_signal.connect(main_window.rcv_dcboard_online_offline_signal)

    configdialog_can.can_device_online_offline_signal.connect(main_window.rcv_can_device_online_offline_signal)

    thread_processdata.update_widget_value_signal.connect(main_window.rcv_update_widget_value_signal)


if __name__ == '__main__':  # 程序的入口
    g_dcboard_offline_cnt = 0
    g_dcboard_offline_flag = False
    #g_can_device_offline_cnt = 0
    g_can_device_offline_flag = True

    g_channel = CanChannel.channel1
    g_can_device = CanDevice()

    app = QApplication(sys.argv)
    main_window = MyMainWindow()
    main_window.show()

    configdialog_can = ConfigCanDialog()
    configdialog_can.show()
    #configdialog_can.exec()
    #configdialog_can.close()

    g_common_data = DcboardCommonData()
    g_version_data = DcboardVersionData()
    g_public_data = DcboardPublicData()
    g_parameter = DcboardParameter()
    g_debug_command = DebugCommand()
    g_protocol = CanProtocol()
    BindDataAndWidget()

    g_thread_list = []
    thread_sendcommand = ThreadSendDcboardCommand()
    g_thread_list.append(thread_sendcommand)
    thread_read_candevice = ThreadCopyDeviceDataToBuff()
    g_thread_list.append(thread_read_candevice)
    thread_send_candevice = ThreadSendBuffDataToDevice()
    g_thread_list.append(thread_send_candevice)
    thread_processdata = ThreadProcessData()
    g_thread_list.append(thread_processdata)
    ConnectSignalSlot()

    for thread in g_thread_list:
        thread.start()
    sys.exit(app.exec_())




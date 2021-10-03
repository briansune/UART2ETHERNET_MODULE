import socket
import serial
import serial.tools.list_ports
import threading
import sys
import os
from time import sleep
from requests import Session, exceptions

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox
)
from PyQt5 import QtGui
from main_window_ui import Ui_oMainWind


# def resource_path(relative_path):
#     base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
#     return os.path.join(base_path, relative_path)


class Window(QMainWindow, Ui_oMainWind):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.sys_ports = []
        self.ui = Ui_oMainWind()
        self.ui.setupUi(self)
        self.connectSignalsSlots()
        self.bStartStopFlag = False
        self.oSocketHolder = None
        self.oSerialHolder = None
        self.oConnectHolder = None
        self.oThreadHolderRx = None
        self.oThreadHolderTx = None

    def connectSignalsSlots(self):
        self.ui.oActInfo.triggered.connect(self.about)
        self.ui.oActExit.triggered.connect(self.close)
        self.ui.oEntryIp0.setText('192')
        self.ui.oEntryIp1.setText('168')
        self.ui.oEntryIp2.setText('16')
        self.ui.oEntryIp3.setText('123')
        self.ui.oEntryPort.setText('5000')
        # self.ui.oLbStatus.setPixmap(QtGui.QPixmap(resource_path("red.png")))
        # self.ui.oLbLargeIcon.setPixmap(QtGui.QPixmap(resource_path("Qorvo_Logo.png")))
        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap(resource_path("qorvo_ico.ico")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        # icon.addPixmap(QtGui.QPixmap(":/qorvo_ico.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        # self.setWindowIcon(icon)

        self.ui.oEntryBaud.setText('57600')
        self.ui.oEntryDataBits.setText('8')
        self.ui.oEntryParityBits.setText('N')
        self.ui.oEntryStopBits.setText('1')
        self.updateComList()
        self.ui.oButStartStop.clicked.connect(self.startStopBind)

    def forceStop(self):
        l_label = ['Stop', 'Start']
        self.bStartStopFlag = False
        self.ui.oButStartStop.setText(l_label[int(not self.bStartStopFlag)])
        self.ui.oListBoxCom.setDisabled(False)
        self.ui.oEntryIp0.setDisabled(False)
        self.ui.oEntryIp1.setDisabled(False)
        self.ui.oEntryIp2.setDisabled(False)
        self.ui.oEntryIp3.setDisabled(False)
        self.ui.oEntryPort.setDisabled(False)
        self.ui.oEntryBaud.setDisabled(False)
        self.ui.oEntryDataBits.setDisabled(False)
        self.ui.oEntryParityBits.setDisabled(False)
        self.ui.oEntryStopBits.setDisabled(False)
        self.closeAll()

    def startStopBind(self):
        l_label = ['Stop', 'Start']
        self.bStartStopFlag = not self.bStartStopFlag
        print('The start flag: {}'.format(self.bStartStopFlag))
        self.ui.oButStartStop.setText(l_label[int(not self.bStartStopFlag)])
        if not self.bStartStopFlag:
            self.ui.oListBoxCom.setDisabled(False)
            self.ui.oEntryIp0.setDisabled(False)
            self.ui.oEntryIp1.setDisabled(False)
            self.ui.oEntryIp2.setDisabled(False)
            self.ui.oEntryIp3.setDisabled(False)
            self.ui.oEntryPort.setDisabled(False)
            self.ui.oEntryBaud.setDisabled(False)
            self.ui.oEntryDataBits.setDisabled(False)
            self.ui.oEntryParityBits.setDisabled(False)
            self.ui.oEntryStopBits.setDisabled(False)
            # self.ui.oLbStatus.setPixmap(QtGui.QPixmap(resource_path("red.png")))
            self.ui.oLbStatus.setPixmap(QtGui.QPixmap(":/red.png"))
            self.closeAll()
        else:
            self.ui.oListBoxCom.setDisabled(True)
            self.ui.oEntryIp0.setDisabled(True)
            self.ui.oEntryIp1.setDisabled(True)
            self.ui.oEntryIp2.setDisabled(True)
            self.ui.oEntryIp3.setDisabled(True)
            self.ui.oEntryPort.setDisabled(True)
            self.ui.oEntryBaud.setDisabled(True)
            self.ui.oEntryDataBits.setDisabled(True)
            self.ui.oEntryParityBits.setDisabled(True)
            self.ui.oEntryStopBits.setDisabled(True)
            # self.ui.oLbStatus.setPixmap(QtGui.QPixmap(resource_path("green.png")))
            self.ui.oLbStatus.setPixmap(QtGui.QPixmap(":/green.png"))
            self.startTcpIpCom()

    def startTcpIpCom(self):

        s_website = r"http://{}.{}.{}.{}".format(
            self.ui.oEntryIp0.text(),
            self.ui.oEntryIp1.text(),
            self.ui.oEntryIp2.text(),
            self.ui.oEntryIp3.text())
        print('Site address: {}'.format(s_website))

        # setup module
        with Session() as o_session:
            try:
                o_site = o_session.get(r"{}/login".format(s_website), timeout=2)

                # login
                o_state = o_session.post(r"{}/state".format(s_website), data={'__PPAS': 'admin'})
                print(o_state.content.decode('gb2312'))

            except exceptions.Timeout:
                # cannot reach
                self.startStopBind()
                return

        o_soc_holder = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        o_soc_holder.connect(("8.8.8.8", 80))
        s_my_ip = o_soc_holder.getsockname()[0]
        o_soc_holder.shutdown(socket.SHUT_RDWR)
        o_soc_holder.close()

        self.oSocketHolder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = (s_my_ip, 60000)
        print(sys.stderr, 'starting up on %s port %s' % server_address)
        self.oSocketHolder.bind(server_address)

        # Listen for incoming connections
        self.oSocketHolder.listen(1)

        self.oSerialHolder = serial.Serial(self.ui.oListBoxCom.currentText(), self.ui.oEntryBaud.text(), timeout=5)
        self.oSerialHolder.close()
        self.oSerialHolder.open()
        self.oConnectHolder, addr = self.oSocketHolder.accept()

        # thread has to start before other loop
        self.oThreadHolderRx = threading.Thread(target=self.recv_msg)
        self.oThreadHolderRx.start()
        self.oThreadHolderTx = threading.Thread(target=self.send_msg)
        self.oThreadHolderTx.start()

    def recv_msg(self):
        while self.bStartStopFlag:
            try:
                recv_msg = self.oConnectHolder.recv(1024)
                if not recv_msg:
                    print('Error occur!')
                    return
                self.oSerialHolder.write(recv_msg)
            except socket.error, exc:
                print('Socket Error {}'.format(exc))
                self.forceStop()
                return

    def send_msg(self):
        while self.bStartStopFlag:
            try:
                send_msg = self.oSerialHolder.read_all()
                send_msg = send_msg.encode()
                self.oConnectHolder.send(send_msg)
            except socket.error, exc:
                print('Socket Error {}'.format(exc))
                self.forceStop()
                return

    def closeAll(self):
        self.oConnectHolder.shutdown(socket.SHUT_RDWR)
        sleep(0.5)
        print self.oThreadHolderRx.isAlive()
        print self.oThreadHolderTx.isAlive()
        self.oSerialHolder.close()

    def updateComList(self):
        self.ui.oListBoxCom.clear()
        l_ports = serial.tools.list_ports.comports()
        connected = [element.device for element in l_ports]
        self.ui.oListBoxCom.addItems(connected)

    def about(self):
        o_msg_box = QMessageBox()
        o_msg_box.setWindowTitle("TCP/IP Serial Binding Tool")
        o_msg_box.setText("<p>Designer: Brfo</p>"
                          "<p>Contact: brian.fong@qorvo.com</p>"
                          "<p>Date: 2021</p>")
        o_msg_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

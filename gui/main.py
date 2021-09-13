import socket
import serial
import serial.tools.list_ports
import threading
import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox
)
from main_window_ui import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.sys_ports = []
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.connectSignalsSlots()
        self.bStartStopFlag = False
        self.oSocketHolder = socket
        self.oSerialHolder = None
        self.oConnectHolder = None
        self.oThreadHolderRx = None
        self.oThreadHolderTx = None

    def connectSignalsSlots(self):
        self.ui.oActInfo.triggered.connect(self.about)
        self.ui.oActExit.triggered.connect(self.close)
        self.ui.oEntryIp0.setText('192')
        self.ui.oEntryIp1.setText('168')
        self.ui.oEntryIp2.setText('xx')
        self.ui.oEntryIp3.setText('xx')
        self.ui.oEntryPort.setText('5000')
        self.ui.oEntryIp0.setDisabled(True)
        self.ui.oEntryIp1.setDisabled(True)
        self.ui.oEntryIp2.setDisabled(True)
        self.ui.oEntryIp3.setDisabled(True)
        self.ui.oEntryPort.setDisabled(True)

        self.ui.oEntryBaud.setText('57600')
        self.ui.oEntryDataBits.setText('8')
        self.ui.oEntryParityBits.setText('N')
        self.ui.oEntryStopBits.setText('1')
        self.updateComList()
        self.ui.oButStartStop.clicked.connect(self.startStopBind)

    def startStopBind(self):
        l_label = ['Stop', 'Start']
        self.bStartStopFlag = not self.bStartStopFlag
        print('The start flag: {}'.format(self.bStartStopFlag))
        self.ui.oButStartStop.setText(l_label[int(not self.bStartStopFlag)])
        if not self.bStartStopFlag:
            self.ui.oListBoxCom.setDisabled(False)
            self.ui.oEntryIp0.setDisabled(True)
            self.ui.oEntryIp1.setDisabled(True)
            self.ui.oEntryIp2.setDisabled(True)
            self.ui.oEntryIp3.setDisabled(True)
            self.ui.oEntryPort.setDisabled(True)
            self.ui.oEntryBaud.setDisabled(False)
            self.ui.oEntryDataBits.setDisabled(False)
            self.ui.oEntryParityBits.setDisabled(False)
            self.ui.oEntryStopBits.setDisabled(False)
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
            self.startTcpIpCom()

    def startTcpIpCom(self):
        self.oSocketHolder = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.oSocketHolder.connect(("8.8.8.8", 80))
        s_my_ip = self.oSocketHolder.getsockname()[0]
        self.oSocketHolder.close()

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
            recv_msg = self.oConnectHolder.recv(1024)
            if not recv_msg:
                print('Error occur!')
                return
            self.oSerialHolder.write(recv_msg)

    def send_msg(self):
        while self.bStartStopFlag:
            send_msg = self.oSerialHolder.read_all()
            send_msg = send_msg.encode()
            self.oConnectHolder.send(send_msg)

    def closeAll(self):
        print self.oThreadHolderRx.isAlive()
        print self.oThreadHolderTx.isAlive()
        self.oSerialHolder.close()
        self.oConnectHolder.close()

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

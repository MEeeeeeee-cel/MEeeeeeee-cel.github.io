#写一个客户端
"""
说明：略

"""
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton,QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile,QTimer#用来加载qt设计好的界面
import socket#用来建立连接
class client:
    def __init__(self):

        self.app = QApplication()#这个一定要放在最前面，这是qt的底层
        qfile_client=QFile(r"D:\PyCharm\pycharm_projects\ui\client.ui")#导入设计好的界面
        qfile_client.open(QFile.ReadOnly)
        qfile_client.close()
        #加载ui
        self.ui=QUiLoader().load(qfile_client)
        self.ui.cancelbutton.clicked.connect(self.cancel_click)#注意不能加括号
        self.ui.sendbutton.clicked.connect(self.send_click)
        self.ui.connectbutton.clicked.connect(self.connect_click)
        self.socket = None
    def showUi(self):
        self.ui.show()
        self.app.exec_()

    def cancel_click(self):
        #退出时及时清理
        if hasattr(self, 'recv_timer'):
            self.recv_timer.stop()
        if self.socket:
            self.socket.close()
        self.ui.close()

    def send_click(self):
        message = self.ui.sendTextEdit.toPlainText()#获取输入信息
        #print(message)
        if not message:
            QMessageBox.warning(self.ui, "警告", "发送内容不能为空！")
        try:
            self.socket.sendall(message.encode('utf-8'))#连接成功后开始发信息
            #QMessageBox.information(self.ui, "提示", "消息已发送！")
        except Exception as e:
            QMessageBox.critical(self.ui, "错误", f"发送失败：{e}")

    def connect_click(self):
        if self.socket:
            self.socket.close()#一定要先关闭，否则会提示你有一个socket
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(3)#防止超时

        self.IP = self.ui.IPlineEdit.text()
        self.Port = int(self.ui.PortlineEdit.text())
        # 超时机制,注意：对全局有效，它会把 所有后续阻塞操作（connect、send、recv、accept…）都变成“限时阻塞”

        try:
            # 如果连接成功
            self.socket.connect((self.IP, self.Port))  # 注意是元组！
            # 这里可以弹个框
            QMessageBox.information(self.ui, "连接信息", "连接成功")
            #开始倾听服务器的内容
            #开启定时器轮询
            self.socket.setblocking(False)  # 设为非阻塞
            self.recv_timer = QTimer(self.ui)#创建定时器
            self.recv_timer.timeout.connect(self.recv_data)#绑定函数
            self.recv_timer.start(200)#200ms轮询一次recdata

        except socket.timeout:
                QMessageBox.warning(self.ui, "连接超时", "3 秒内未建立连接，请检查服务器是否开")
        except socket.error as e:
                QMessageBox.critical(self.ui, "连接失败", f"无法连接到服务器：\n{e}")
        print("connect")


    def recv_data(self):
        if not self.socket:
            return
        try:
            data = self.socket.recv(1024)
            if not data:                # 对方正常关闭
                self.recv_timer.stop()#停止接收数据
                QMessageBox.information(self.ui, "连接断开", "服务器已关闭")
                return
            # 追加显示
            self.ui.reciveTextEdit.append(data.decode('utf-8'))#用append不会清除，如果用set会清除原来的信息

        except (BlockingIOError, ConnectionResetError, OSError):
            pass   # 暂无数据或已重置，下轮再试,表示对方没有发送数据



#实例化
myUi=client()
myUi.showUi()




















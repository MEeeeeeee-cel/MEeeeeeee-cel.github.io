#写一个服务端
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton,QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile,QTimer#用来加载qt设计好的界面
import socket#用来建立连接
class server:
    def __init__(self,IP,Port):
        self.listenIP=IP
        self.listenPort=Port
        self.app = QApplication()#这个一定要放在最前面，这是qt的底层
        qfile_client=QFile(r"D:\PyCharm\pycharm_projects\ui\server.ui")#导入设计好的界面
        qfile_client.open(QFile.ReadOnly)
        qfile_client.close()
        #加载ui
        self.ui=QUiLoader().load(qfile_client)
        self.ui.cancelbutton.clicked.connect(self.cancel_click)#注意不能加括号
        self.ui.sendbutton.clicked.connect(self.send_click)
        #开始监听按钮和停止监听按钮
        self.ui.listenbutton.clicked.connect(self.startListen)
        self.ui.stopListenbutton.clicked.connect(self.stopListen)

        #self.ui.connectbutton.clicked.connect(self.connect_click)
        # 创建socket对象使用 IPv4 #地址（如 192.168.1.10）,使用TCP协议
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #监听
        self.listen_socket = None#服务器自己的socket
        self.client_socket = None#用来接收客户的socke


    def showUi(self):
        self.ui.show()
        self.app.exec_()

    def cancel_click(self):
        #释放资源
        self.socket.close()
        self.listen_timer.stop()
        self.recv_timer.stop()
        self.ui.close()

    def send_click(self):
        message = self.ui.sendTextEdit.toPlainText()#获取输入信息
        #print(message)
        if not message:
            QMessageBox.warning(self.ui, "警告", "发送内容不能为空！")
        try:
            self.socket.sendall(message.encode('utf-8'))
            QMessageBox.information(self.ui, "提示", "消息已发送！")
        except Exception as e:
            QMessageBox.critical(self.ui, "错误", f"发送失败：{e}")

    def startListen(self):
        #print("listen")
        try:
            self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listen_socket.bind((self.listenIP, self.listenPort))
            self.listen_socket.setblocking(False)
            self.listen_socket.listen(1)#这个地方方开始已经在倾听了
        except Exception as e:
            QMessageBox.critical(self.ui, "监听失败", str(e))
            return
        QMessageBox.information(self.ui, "监听信息","监听中.....")



        # 计时器：反复尝试 accept
        self.listen_timer = QTimer(self.ui)
        self.listen_timer.timeout.connect(self.try_accept)  # 绑定轮询函数
        self.listen_timer.start(200)


    def try_accept(self):
        try:
            self.client_socket, addr = self.listen_socket.accept()#这个返回的是客户端的ip
            self.client_socket.setblocking(False)
            QMessageBox.information(self.ui, "监听信息", "监听成功")
            self.listen_timer.stop()  # 停止轮询，关闭定时器

            #如果成功获取，客户端的ip和端口号
            self.ui.IPline.setText(addr[0])

            self.ui.Portline.setText(str(addr[1]))
            #连接成功后开始接收数据
            self.recv_timer=QTimer(self.ui)
            self.recv_timer.timeout.connect(self.recv_data)  # 连接成功后，绑定接收数据函数
            self.recv_timer.start(10)  #  每 200ms 自动触发
            # 后续再启动接收定时器...
        except socket.error:
            pass  # 还没连入，继续等

    def send_click(self):


        #print("stopListen")
        message = self.ui.sendTextEdit.toPlainText()  # 获取输入信息
        # print(message)
        if not message:
            QMessageBox.warning(self.ui, "警告", "发送内容不能为空！")
        try:
            self.client_socket.sendall(message.encode('utf-8'))  # 连接成功后开始发信息
            # QMessageBox.information(self.ui, "提示", "消息已发送！")
        except Exception as e:
            QMessageBox.critical(self.ui, "错误", f"发送失败：{e}")

    def recv_data(self):
        if not self.client_socket:
            return
        try:
            data = self.client_socket.recv(1024)
            if not data:                      # 客户端正常关闭
                self.recv_timer.stop()
                QMessageBox.information(self.ui, "连接断开", "客户端已断开")
                self.client_socket.close()
                self.client_socket = None
                return
            # 追加显示
            self.ui.reciveTextEdit.append(data.decode('utf-8'))
        except (BlockingIOError, ConnectionResetError, OSError):
            # 暂无数据或已重置，下轮再试
            pass
    def stopListen(self):
        self.listen_timer.stop()
        if self.client_socket:
            self.client_socket.close()
        if self.listen_socket:
            self.listen_socket.close()
#实例化
myUi=server(IP='0.0.0.0',Port=8000)#0000表示监听所有的地址

myUi.showUi()





























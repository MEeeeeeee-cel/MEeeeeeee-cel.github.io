import threading
import time

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton,QMessageBox,QDialog, QSpinBox, QDialogButtonBox, QFormLayout
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile,QTimer,QThread,Signal#用来加载qt设计好的界面
import socket#用来建立连接
from PySide2 import  QtWidgets

#多线程：多任务同时运行
#把以下代码改成多线程
import requests
from urllib.request import urlopen
from PySide2.QtGui import QIcon#加入图标函数
from datetime import datetime      #获取当前时间
class mytime():
    def __init__(self):
        self.app = QApplication()  # 这个一定要放在最前面，这是qt的底层
        qfile_client = QFile(r"D:\PyCharm\pycharm_projects\ui\http.ui")  # 导入设计好的界面
        qfile_client.open(QFile.ReadOnly)
        qfile_client.close()
        # 加载ui
        self.ui = QUiLoader().load(qfile_client)
        self.ui.exitbutton.clicked.connect(self.exitUi)
        self.ui.addHeadbutton.clicked.connect(self.addHead)
        self.ui.deletHeadbutton.clicked.connect(self.deletHead)
        self.ui.sendbutton.clicked.connect(self.sendClick)
        self.timeThread=TimeWorker()
        self.timeThread.timeSignal.connect(self.ui.TimelineEdit.setText)
        self.timeThread.start()
        # #不要忘记target=
        # self.timeThread=threading.Thread(target=self.timeThread)#创建多线程对象，括号里面是绑定的线程功能
        # self.timeThread.timeSignal.connect(self.ui.TimelineEdit.setText)#主线程和子线程的连接桥梁
        # self.timeThread.start()#开始启动多线程,线程一旦启用，无法退出，只能考条件协作让其不运行


    def showUi(self):
        #给界面左上角加上图标
        self.app.setWindowIcon(QIcon(r"D:\PyCharm\pycharm_projects\tupian\yangzi.jpg"))#给你自己的图片
        self.ui.show()
        self.app.exec_()
    def exitUi(self):
        self.ui.close()
        exit(0)
    def addHead(self):
        # 设置行列
        # object.ui.messageHeadtableWidget.setRowCount(2)#在
        # object.ui.messageHeadtableWidget.setColumnCount(1)#在二行一列设置内容
        #添加新行
        row = self.ui.messageHeadtableWidget.rowCount()  # 当前总行数
        #print(row)
        self.ui.messageHeadtableWidget.insertRow(row)  # 在末尾插入一空行,内容可自己编写

    def deletHead(self):
        #删除选定的行
        table = self.ui.messageHeadtableWidget
        row = table.currentRow()  # 获取当前选中的行
        if row == -1:  # 表示是列表
            QMessageBox.information(self.ui, "提示", "请先选中要删除的行！")
            return
        table.removeRow(row)  # 立即删除

    def sendClick(self):

        #发送的时候先判断一下是什么请求方式
        method = self.ui.httpcomboBox.currentText().upper()#获取当前模式
        print(method)


        url = self.ui.httplineEdit.text().strip()
        if not url:
            return
        if method=="GET":
            try:
                with urlopen(url) as resp:
                    html = resp.read().decode('utf-8')  # ① 读取字节 ② 解码成 str
                    self.ui.requestextEdit.setPlainText(html)
            except Exception as e:
                self.ui.requestextEdit.setPlainText(f'请求失败：{e}')
        elif method=="POST":
            try:
                data = {'kw': "dog"}
                # 发送POST请求
                response = requests.post(url=url, data=data)
                response = response.text

                self.ui.requestextEdit.setPlainText(response)
            except Exception as e:
                self.ui.requestextEdit.setPlainText(f'请求失败：{e}')




#创建一个线程
class TimeWorker(QThread):#继承了QTHREAD
    timeSignal = Signal(str)          # 信号定义在 Qt 线程里
    def run(self):
        while True:
            self.timeSignal.emit(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))   # 发射给主线程
            QThread.msleep(500)       # 非阻塞延时

#获取当时时间
# now = datetime.now()
# year   = now.year      # 年
# month  = now.month     # 月
# day    = now.day       # 日
# hour   = now.hour      # 时
# minute = now.minute    # 分
# second = now.second    # 秒

# print(year, month, day, hour, minute, second)
object=mytime()

object.showUi()

#pyinstaller httpclient.py --noconsole --hidden-import PySide6.QtXml:在命令行输入该指定，可以生成exe程序



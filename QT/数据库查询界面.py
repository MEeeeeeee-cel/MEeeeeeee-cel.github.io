import time
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton,QMessageBox,QDialog, QSpinBox, QDialogButtonBox, QFormLayout
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile,QTimer,QThread,Signal#用来加载qt设计好的界面
from PySide2 import  QtWidgets
from datetime import datetime      #获取当前时间
import pymysql

class mysqlUi():
    def __init__(self):
        self.app = QApplication()  # 这个一定要放在最前面，这是qt的底层
        qfile_mysql = QFile(r"D:\PyCharm\pycharm_projects\ui\mysqlUi.ui")  # 导入设计好的界面
        qfile_mysql.open(QFile.ReadOnly)
        qfile_mysql.close()
        # 加载ui
        self.ui = QUiLoader().load(qfile_mysql)
        #设置背景图
        self.ui.setObjectName("mainWindow")  # 用于样式表选择器
        self.ui.setStyleSheet(r"""
                   #mainWindow{
                       border-image: url(D:/PyCharm/pycharm_projects/tupian/xiao.jpg) 0 0 0 0 stretch stretch;
                   }
               """)



        self.mysql80=None       #用来获取数据库信息的变量
        self.ConnectFlag=False
        self.dataInformation=None       #存放从数据库中获取的信息
        self.ui.exitbutton.clicked.connect(self.exitUi)
        #okay，cancel的选择
        self.ui.ensurebutton.clicked.connect(self.ensureClicked)
        self.ui.buttonBox.accepted.connect(self.executiveSqlOrder)
        self.ui.buttonBox.rejected.connect(self.clearAll)
        #创建线程
        self.trans_thread=trans_thread()
        self.trans_thread.dataSignal.connect(self.ui.sqltextEdit.setPlainText)
        #self.dataTrans.start()#等待执行指令才开启线程

        # self.timeThread=TimeWorker()
        # self.timeThread.timeSignal.connect(self.ui.TimelineEdit.setText)
        # self.timeThread.start()
        # #不要忘记target=
        # self.timeThread=threading.Thread(target=self.timeThread)#创建多线程对象，括号里面是绑定的线程功能
        # self.timeThread.timeSignal.connect(self.ui.TimelineEdit.setText)#主线程和子线程的连接桥梁
        # self.timeThread.start()#开始启动多线程,线程一旦启用，无法退出，只能考条件协作让其不运行


    def showUi(self):
        self.ui.show()
        self.app.exec_()
    def exitUi(self):
        self.ui.close()
    def ensureClicked(self):
        print("执行指令")
        hostip=self.ui.iplineEdit.text()
        port=int(self.ui.portlineEdit.text())
        userName=self.ui.userNamelineEdit.text()
        password = self.ui.passwordlineEdit.text()
        database=self.ui.databaselineEdit.text()
        encoding=self.ui.encodelineEdit.text()

        #在qt中已经设定了默认值，不输入连接到默认的用户（我的linux）
        try:
            connect = pymysql.connect(
                host=hostip,  # 虚拟机 IP
                port=port,
                user=userName,
                password=password,
                database=database,
                charset=encoding
            )
            self.ConnectFlag=True
            self.mysql80=connect.cursor()
            QMessageBox.information(self.ui, "成功", "数据库已连接！")
        except Exception as e:
            self.ConnectFlag = False
            QMessageBox.warning(self.ui, "连接失败", f"无法连接数据库：\n{e}")

    def executiveSqlOrder(self):
        if not self.ConnectFlag:
            QMessageBox.warning(self.ui, "提示", "尚未成功连接数据库！")
            return
        try:
            self.mysql80.execute(self.ui.sqlOrdertextEdit.toPlainText())
            #获取返回信息
            self.dataInformation=self.mysql80.fetchall()
            #print(self.dataInformation)
            #数据显示使用了线程
            #self.ui.sqltextEdit.setPlainText(str(self.dataInformation[0][1]))

            # 拿数据和列名
            cols = [col[0] for col in self.mysql80.description]
            print(cols)
            # 交给线程转换
            self.trans_thread.set_data(self.dataInformation, cols)
            self.trans_thread.start()  # 触发 run()
        except Exception as e:
            QMessageBox.warning(self.ui, "指令错误", f"执行失败：\n{e}")
    def clearAll(self):
        self.ui.sqlOrdertextEdit.clear()



#开一个线程来将数据转换为字符串
class trans_thread(QThread):
    dataSignal = Signal(str)
    GAP = 12  # 列间空格数，可改 10/14 等

    # —— 1. 主线程塞数据 ——
    def set_data(self, rows, cols):
        self.rows = rows
        self.cols = cols

    # —— 2. 后台转字符串 ——
    def run(self):
        if not self.rows or not self.cols:
            self.dataSignal.emit("")
            return

        # 计算每列最大宽度（含表头）
        col_width = [len(c) for c in self.cols]
        for row in self.rows:
            for i, cell in enumerate(row):
                col_width[i] = max(col_width[i], len(str(cell)))

        lines = []

        # 表头
        head = "".join(c.ljust(col_width[i] + self.GAP)
                      for i, c in enumerate(self.cols)).rstrip()
        lines.append(head)

        # 下划线（长度 = 表头可视长度）
        underline = "-" * len(head)
        lines.append(underline)

        # 数据行
        for row in self.rows:
            line = "".join(str(cell).ljust(col_width[i] + self.GAP)
                          for i, cell in enumerate(row)).rstrip()
            lines.append(line)

        # 发回主线程
        self.dataSignal.emit("\n".join(lines))


object=mysqlUi()
object.showUi()



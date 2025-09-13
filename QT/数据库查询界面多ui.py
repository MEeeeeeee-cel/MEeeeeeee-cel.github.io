import time
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton,QMessageBox,QDialog, QSpinBox, QDialogButtonBox, QFormLayout
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile,QTimer,QThread,Signal#用来加载qt设计好的界面
from PySide2 import  QtWidgets
from datetime import datetime      #获取当前时间
import pymysql
import re
erroList=["原信息为空","请输入","无法匹配"]
class mysqlUi():
    def __init__(self):
        self.app = QApplication()  # 这个一定要放在最前面，这是qt的底层
        qfile_mysql = QFile(r"D:\PyCharm\pycharm_projects\ui\sqlLogin.ui")  # 导入设计好的界面
        qfile_mysql.open(QFile.ReadOnly)
        qfile_mysql.close()
        # 加载ui
        self.ui = QUiLoader().load(qfile_mysql)
        # #设置背景图
        # self.ui.setObjectName("mainWindow")  # 用于样式表选择器
        # self.ui.setStyleSheet(r"""
        #            #mainWindow{
        #                border-image: url(D:/PyCharm/pycharm_projects/tupian/xiao.jpg) 0 0 0 0 stretch stretch;
        #            }
        #        """)



        self.mysql80=None       #用来获取数据库信息的变量
        self.ConnectFlag=False
        self.dataInformation=None       #存放从数据库中获取的信息
        self.ui.exitbutton.clicked.connect(self.exitUi)
        #okay，cancel的选择
        self.ui.ensurebutton.clicked.connect(self.ensureClicked)#确认登录

        # self.ui.buttonBox.accepted.connect(self.executiveSqlOrder)
        # self.ui.buttonBox.rejected.connect(self.clearAll)
        #创建线程

        #self.trans_thread.dataSignal.connect(self.ui.sqltextEdit.setPlainText)
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
        print("登录中.....")
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
            self.exitUi()
            qfile_mysql = QFile(r"D:\PyCharm\pycharm_projects\ui\sqlOrder.ui")  # 导入设计好的界面
            qfile_mysql.open(QFile.ReadOnly)
            qfile_mysql.close()
            # 加载ui
            self.ui = QUiLoader().load(qfile_mysql)
            # # 设置背景图
            # self.ui.setObjectName("mainWindow")  # 用于样式表选择器
            # self.ui.setStyleSheet(r"""
            #                    #mainWindow{
            #                        border-image: url(D:/PyCharm/pycharm_projects/tupian/xiao.jpg) 0 0 0 0 stretch stretch;
            #                    }
            #                """)
            self.ui.buttonBox.accepted.connect(self.executiveSqlOrder)
            self.ui.buttonBox.rejected.connect(self.clearAll)
            self.trans_thread = trans_thread()
            self.trans_thread.dataSignal.connect(self.ui.sqltextEdit.setPlainText)
            self.search_thread=search_thread()
            self.search_thread.searchSignal.connect(self.searchThread)

            self.ui.exitbutton.clicked.connect(self.exitUi)
            self.ui.searchbutton.clicked.connect(self.searchClicked)

            self.showUi()
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
            self.cols = [col[0] for col in self.mysql80.description]
            print(self.cols )
            # 交给线程转换
            self.trans_thread.set_data(self.dataInformation, self.cols)
            self.trans_thread.start()  # 发一次指令触发一次线程
        except Exception as e:
            QMessageBox.warning(self.ui, "指令错误", f"执行失败：\n{e}")
    def clearAll(self):
        self.ui.sqlOrdertextEdit.clear()
    def searchClicked(self):
        keywords=self.ui.searchlineEdit.text()
        keywords=str.lower(keywords)
        self.search_thread.set_data(self.dataInformation,keywords,self)
        self.search_thread.start()
        #把keywords 放到self.ui.sqltextEdit.toPlainText 比较，找到我们需要的内容
        #后把数据显示在 searchtextEdit，使用指令elf.ui.searchtextEdit.toPlainText
    def searchThread(self,message):#这个message就是emi发送过来的数据
        if message in erroList:
            QMessageBox.warning(self.ui, "查询警告", message)
            return
        self.ui.searchtextEdit.setPlainText(message)
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





# #查询线程
# class search_thread(QThread):
#     searchSignal = Signal(str)
#
#     # —— 1. 主线程塞数据 ——
#     def set_data(self, information, keywords):
#         self.information = information
#         self.keywords = keywords
#
#     # —— 2. 后台转字符串 ——
#     def run(self):
#         self.searchSignal.emit("检索到的信息")
#         time.sleep(1)
class search_thread(QThread):
    searchSignal = Signal(str)

    def set_data(self, information, keywords,main):
        self.information = information
        self.keywords = keywords
        self.main=main
    def run(self):
        if not self.information:
            self.searchSignal.emit(erroList[0])
            return
        if not self.keywords:
            self.searchSignal.emit(erroList[1])
            return
        # 1. 编译正则，忽略大小写
        try:
            pattern = re.compile(self.keywords, re.I)
        except re.error:
            pattern = re.compile(re.escape(self.keywords), re.I)

        # 2. 过滤命中行
        hit_rows = [
            row for row in self.information
            if any(pattern.search(str(cell)) for cell in row)
        ]

        if not hit_rows:
            self.searchSignal.emit(erroList[2])
            return

        # 3. 列名从主线程拿（主线程已保存 self.cols）

        cols =self.main.cols

        # 4. 以下对齐算法与 trans_thread 完全一致
        GAP = 12
        col_width = [len(c) for c in cols]
        for row in hit_rows:
            for i, cell in enumerate(row):
                col_width[i] = max(col_width[i], len(str(cell)))

        lines = []
        head = "".join(c.ljust(col_width[i] + GAP) for i, c in enumerate(cols)).rstrip()
        lines.append(head)
        lines.append("-" * len(head))
        for row in hit_rows:
            line = "".join(str(cell).ljust(col_width[i] + GAP) for i, cell in enumerate(row)).rstrip()
            lines.append(line)

        self.searchSignal.emit("\n".join(lines))


object=mysqlUi()
object.showUi()







from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QHeaderView, QWidget, QDialog
import matplotlib.pyplot as plt
import pandas as pd
import pyqtgraph as pg
from SimulateStablePRI import GenerateStablePRI
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
#import IP


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
    def setupUi(self, MainWindow ):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1900, 980)
        MainWindow.setMaximumSize(1900,980)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        ######################################        Creating Table Widget       ######################################
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(50, 70, 860, 880))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.tableWidget.setFont(font)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        # self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setHorizontalHeaderLabels(
            ("PW", " PA ", " PRI ", " Classification "))
        self.tableWidget.setStatusTip("Table widget")
        #self.tableWidget.setRowCount(0)

        self.Graph1 = pg.PlotWidget(self.centralwidget)
        self.Graph1.setGeometry(QtCore.QRect(1000, 70, 850, 280))
        self.Graph1.setObjectName("Graph3")
        self.Graph1.setLabel('left', 'Count')
        self.Graph1.setLabel('bottom', 'TOA')

        self.Graph2 = pg.PlotWidget(self.centralwidget)
        self.Graph2.setGeometry(QtCore.QRect(1000, 370, 850, 280))
        self.Graph2.setObjectName("Graph3")
        self.Graph2.setLabel('left', 'Count')
        self.Graph2.setLabel('bottom', 'TOA')

        self.Graph3 = pg.PlotWidget(self.centralwidget)
        self.Graph3.setGeometry(QtCore.QRect(1000, 670, 850, 280))
        self.Graph3.setObjectName("Graph3")
        self.Graph3.setLabel('left', 'Count')
        self.Graph3.setLabel('bottom', 'TOA')

        MainWindow.setCentralWidget(self.centralwidget)

        ############################################## Status Bar  ####################################################
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        ##############################################   Tool Bar  ####################################################
        self.toolbar = QtWidgets.QToolBar(MainWindow)
        self.toolbar.setObjectName("toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setGeometry(QtCore.QRect(0,0,1900,50))
        self.toolbar.setIconSize(QtCore.QSize(60,60))
        self.toolbar.addSeparator()

        ######################################    Creating Tool Bar Icons #################################################
        self.btn1 = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.btn1.setText("Stable")
        self.btn1.setFont(font)
        self.toolbar.addAction(self.btn1)

        self.btn2 = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.btn2.setText("Staggered")
        self.btn2.setFont(font)
        self.toolbar.addAction(self.btn2)

        self.btn3 = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.btn3.setText("Jitter")
        self.btn3.setFont(font)
        self.toolbar.addAction(self.btn3)

        self.btn4 = QtWidgets.QAction(MainWindow)
        self.btn4.setIcon(QtGui.QIcon(""))
        self.toolbar.addAction(self.btn4)

        self.tableWidget.rowCount()
        self.df = pd.read_csv("pdw.csv")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.btn1.triggered.connect(self.Window1)
        self.btn2.triggered.connect(self.Window2)
        self.btn3.triggered.connect(self.Window3)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    def Window1(self):
        StbPRIDlg = GenerateStablePRI()
       # StbPRIDlg.trail = False
       # self.Wd1.show()
        StbPRIDlg.exec()
        print(StbPRIDlg.trail)
        print(StbPRIDlg.threat_df)
    def Window2(self):
        self.Wd2 = Tool2_Window()
        self.Wd2.show()
    def Window3(self):
        self.Wd3 = Tool3_Window()
        self.Wd3.show()

    def Exit(self):
        reply = QMessageBox.question(self, 'Confirm Exit', 'Are you sure you want to exit Hub Configuration?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            quit()

class Tool2_Window(QMainWindow):
    def __init__(self):
        super(Tool2_Window, self).__init__()
        self.setWindowTitle("Staggered PRI")
        self.resize(1050,630)
        self.setMaximumSize(1050,630)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.label_SL = QtWidgets.QLabel("Staggered Level", self)
        self.label_SL.setGeometry(QtCore.QRect(110,50,160,31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_SL.setFont(font)

        self.lineEdit_SL = QtWidgets.QLineEdit(self)
        self.lineEdit_SL.setGeometry(QtCore.QRect(300,50,100,31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_SL.setFont(font)

        self.label_MP = QtWidgets.QLabel("% Missing Pulse", self)
        self.label_MP.setGeometry(QtCore.QRect(110, 120, 160, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_MP.setFont(font)

        self.lineEdit_MP = QtWidgets.QComboBox(self)
        self.lineEdit_MP.setGeometry(QtCore.QRect(300, 120, 100, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_MP.setFont(font)
        self.lineEdit_MP.addItems(
            ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"])

        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(100, 160, 850, 410))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.tableWidget.setFont(font)
        self.tableWidget.setColumnCount(2)
        # self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setHorizontalHeaderLabels(
            ("Pulse Width", " PRI "))

        self.PB_M = QtWidgets.QPushButton(" Done", self)
        self.PB_M.setGeometry(QtCore.QRect(470,575,130,40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.PB_M.setFont(font)
        self.PB_M.setIcon(QtGui.QIcon("done.png"))
        self.PB_M.setIconSize(QtCore.QSize(20, 20))

        self.lineEdit_MP.activated.connect(self.rows)
    def rows(self):
        self.tableWidget.setRowCount(int(self.lineEdit_MP.currentText()))

class Tool3_Window(QMainWindow):
    def __init__(self):
        super(Tool3_Window, self).__init__()
        self.setWindowTitle("Jitter")
        self.resize(500,330)
        self.setMaximumSize(500,330)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.label_PRI = QtWidgets.QLabel("PRI", self)
        self.label_PRI.setGeometry(QtCore.QRect(100,50,100,31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_PRI.setFont(font)

        self.lineEdit_PRI = QtWidgets.QLineEdit(self)
        self.lineEdit_PRI.setGeometry(QtCore.QRect(210,50,100,31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_PRI.setFont(font)

        self.label_J = QtWidgets.QLabel("Jitter", self)
        self.label_J.setGeometry(QtCore.QRect(100, 120, 100, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_J.setFont(font)

        self.lineEdit_J = QtWidgets.QComboBox(self)
        self.lineEdit_J.setGeometry(QtCore.QRect(210, 120, 100, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_J.setFont(font)
        self.lineEdit_J.addItems(["Lock On","Circular","Sector Scan"])

        self.label_MP = QtWidgets.QLabel("% Missing Pulse", self)
        self.label_MP.setGeometry(QtCore.QRect(100, 190, 160, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_MP.setFont(font)

        self.lineEdit_MP = QtWidgets.QComboBox(self)
        self.lineEdit_MP.setGeometry(QtCore.QRect(280, 190, 100, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_MP.setFont(font)
        self.lineEdit_MP.addItems(
            ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"])

        self.PB_P = QtWidgets.QPushButton(" Done", self)
        self.PB_P.setGeometry(QtCore.QRect(200, 260, 130, 40))
        self.PB_P.setFont(font)
        self.PB_P.setIcon(QtGui.QIcon("done.png"))
        self.PB_P.setIconSize(QtCore.QSize(20,20))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

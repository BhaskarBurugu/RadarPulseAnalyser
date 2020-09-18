################################################################################################################
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QHeaderView
import matplotlib.pyplot as plt
import pandas as pd
import pyqtgraph as pg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from RadarPulseAnalyser import MyThread
################################################################################################################
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
        self.tableWidget.setGeometry(QtCore.QRect(50, 540, 850, 300))
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
        #######################################       Creating Pushbutton   ############################################
        self.pushButton_Start = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_Start.setGeometry(QtCore.QRect(400, 870, 180, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        self.pushButton_Start.setFont(font)
        self.pushButton_Start.setStyleSheet("border-top-color: rgb(144, 255, 248);\n"
"border-bottom-color: rgb(157, 255, 121);")
        self.pushButton_Start.setObjectName("pushButton_Start")
        ######################################## Creating Widgets(Plotting Graphs) ####################################
        self.Graph1 = pg.PlotWidget(self.centralwidget)
        self.Graph1.setGeometry(QtCore.QRect(50, 80, 850, 410))
        self.Graph1.setLabel('left', 'PRI')
        self.Graph1.setLabel('bottom', 'Pulse Count')

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.Graph2 = pg.LayoutWidget(self.centralwidget)
        self.Graph2.setGeometry(QtCore.QRect(1000, 80, 850, 410))
        self.Graph2.addWidget(self.canvas)
        self.Graph2.addWidget(self.toolbar)

        self.Dialer = QtWidgets.QDial(self.centralwidget)
        self.Dialer.setGeometry(QtCore.QRect(1640, 300, 150, 150))
        self.Dialer.setNotchesVisible(True)
       # self.Dialer.setWrapping(True)
        self.Dialer.setMinimum( 1 )
        self.Dialer.setMaximum( 100 )

        self.Graph3 = pg.PlotWidget(self.centralwidget)
        self.Graph3.setGeometry(QtCore.QRect(1000, 520, 850, 410))
        self.Graph3.setObjectName("Graph3")
        self.Graph3.setLabel('left', 'Count')
        self.Graph3.setLabel('bottom', 'TOA')

        ## Set Graph background colour ( White-'w',Black-'k',Green-'g',Red-'r',Yellow-'y',Blue-'b',cyan (bright blue-green)-'c',magenta (bright pink)-'m' ) ###########
        self.Graph1.setBackground('k')
        #self.Graph2.setBackground('k')
        self.Graph3.setBackground('k')

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
        self.btn1.setIcon(QtGui.QIcon("IP.png"))
        self.btn1.setObjectName("btn1")
        self.toolbar.addAction(self.btn1)

        self.btn2 = QtWidgets.QAction(MainWindow)
        self.btn2.setIcon(QtGui.QIcon("pulse1.png"))
        self.btn2.setObjectName("btn2")
        self.toolbar.addAction(self.btn2)

        self.btn3 = QtWidgets.QAction(MainWindow)
        self.btn3.setIcon(QtGui.QIcon(""))
        self.btn3.setObjectName("btn3")
        self.toolbar.addAction(self.btn3)

        self.btn4 = QtWidgets.QAction(MainWindow)
        self.btn4.setIcon(QtGui.QIcon(""))
        self.btn4.setObjectName("btn4")
        self.toolbar.addAction(self.btn4)

        self.pushButton_Start.clicked.connect(self.StartPA)
        self.Dialer.valueChanged.connect(self.Plot_DTOA)
        self.btn1.triggered.connect(self.Window1)
        self.btn2.triggered.connect(self.Window2)
        self.tableWidget.rowCount()
        self.df = pd.read_csv("pdw.csv")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.thread = MyThread()
       # self.thread.change_value.connect(self.setProgressVal)
        self.thread.StopFlag = False
        self.thread.start()
        self.thread.StartPulseAnalysis = False
        self.thread.pd_PDW_Update.connect(self.updateGraphs)
        self.thread.Track_Update.connect(self.updateTrackTable)
       # Track_Update = pyqtSignal(bytearray)

    def StartPA(self):
        if self.thread.StartPulseAnalysis == False :
            self.pushButton_Start.setText("Stop PA")
            self.thread.StartPulseAnalysis = True

        elif self.thread.StartPulseAnalysis == True:
            self.pushButton_Start.setText("Start PA")
            self.thread.StartPulseAnalysis = False

    def updateGraphs(self,df_Pdw):
        print('Update Graphs')
        print(df_Pdw.head())
#Munny write here for Graphs updation
    def updateTrackTable(self,TrackData):
        print('Update Table')
        print(TrackData)
        #Munny Write here for Tbale updation

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_Start.setText(_translate("MainWindow", "Start PA"))

    def Window1(self):
        self.Wd1 = Tool1_Window()
        self.Wd1.show()
    def Window2(self):
        self.Wd2 = Tool2_Window()
        self.Wd2.show()
    def Plot_DTOA(self):
        pen1 = pg.mkPen(color=(0, 150, 0), width=3, style=QtCore.Qt.SolidLine)
        TOA = self.df['TOA']
        PW = self.df['PW']
        PA = self.df['PA']
        PC = self.df['PC']
        DTOA = self.df['DTOA']
        #print(PA)
        self.Graph1.plot( PC , DTOA, pen=pen1)
        #self.Graph1.setYRange()

        x_lim = self.Dialer.value() * 1000
        #print("count", x_lim)
        y = []
        #for index in range(10):
        cur_TOA = 0
        index = 0
        while cur_TOA < x_lim:
            for t in range(TOA[index] , TOA[index] + PW[index]):
                y.append(1)
            for t in range( TOA[index] + PW[index] , TOA[index + 1]):
                y.append(0)
            cur_TOA = TOA[index + 1]
            index = index+1
        x = [*range(0, len(y), 1)]
        plt.plot(x, y, "g")
        plt.title('DTOA vs Pulse Count')
        plt.ylabel('DTOA (micro sec)')
        plt.xlabel('Pulse Count->')
        plt.xlim(0, x_lim)
        plt.ylim(-1, +5)
       # plt.hlines(y=0, xmin=0, xmax=4000, linewidth=1, color='k', linestyles="--")
        self.canvas.draw()

    def Exit(self):
        reply = QMessageBox.question(self, 'Confirm Exit', 'Are you sure you want to exit Hub Configuration?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            quit()
###############################################################################################################
class Tool1_Window(QMainWindow):
    def __init__(self):
        super(Tool1_Window,self).__init__()
        self.setWindowTitle("Modify IP")
        self.resize(550,500)
        self.setMaximumSize(550,500)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.label_IP = QtWidgets.QLabel("IP address", self)
        self.label_IP.setGeometry(QtCore.QRect(130,50,160,31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_IP.setFont(font)

        self.lineEdit_IP = QtWidgets.QLineEdit(self)
        self.lineEdit_IP.setGeometry(QtCore.QRect(280,50,160,31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_IP.setFont(font)
        self.lineEdit_IP.setAlignment(QtCore.Qt.AlignHCenter)
        self.lineEdit_IP.setInputMask("000.000.000.000")

        self.label_SM = QtWidgets.QLabel("Subnet Mask", self)
        self.label_SM.setGeometry(QtCore.QRect(130,120,160,31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_SM.setFont(font)

        self.lineEdit_SM = QtWidgets.QLineEdit(self)
        self.lineEdit_SM.setGeometry(QtCore.QRect(280, 120, 160, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_SM.setFont(font)
        self.lineEdit_SM.setAlignment(QtCore.Qt.AlignHCenter)
        self.lineEdit_SM.setInputMask("000.000.000.000")

        self.label_SI = QtWidgets.QLabel("Server IP", self)
        self.label_SI.setGeometry(QtCore.QRect(130, 190, 160, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_SI.setFont(font)

        self.lineEdit_SI = QtWidgets.QLineEdit(self)
        self.lineEdit_SI.setGeometry(QtCore.QRect(280, 190, 160, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_SI.setFont(font)
        self.lineEdit_SI.setAlignment(QtCore.Qt.AlignHCenter)
        self.lineEdit_SI.setInputMask("000.000.000.000")

        self.label_GW = QtWidgets.QLabel("Gate Way", self)
        self.label_GW.setGeometry(QtCore.QRect(130, 260, 160, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_GW.setFont(font)

        self.lineEdit_GW = QtWidgets.QLineEdit(self)
        self.lineEdit_GW.setGeometry(QtCore.QRect(280, 260, 160, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_GW.setFont(font)
        self.lineEdit_GW.setAlignment(QtCore.Qt.AlignHCenter)
        self.lineEdit_GW.setInputMask("000.000.000.000")

        self.label_PN = QtWidgets.QLabel("Port Number", self)
        self.label_PN.setGeometry(QtCore.QRect(130, 330, 160, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_PN.setFont(font)

        self.lineEdit_PN = QtWidgets.QLineEdit(self)
        self.lineEdit_PN.setGeometry(QtCore.QRect(280, 330, 160, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_PN.setFont(font)

        self.PB_P = QtWidgets.QPushButton("Proceed", self)
        self.PB_P.setGeometry(QtCore.QRect(200, 400, 150, 40))
        self.PB_P.setFont(font)
################################################################################################################
class Tool2_Window(QMainWindow):
    def __init__(self):
        super(Tool2_Window, self).__init__()
        self.setWindowTitle("Noise Floor Measurement")
        self.resize(1050,630)
        self.setMaximumSize(1050,630)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.label_SP = QtWidgets.QLabel("Select Port", self)
        self.label_SP.setGeometry(QtCore.QRect(110,50,160,31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_SP.setFont(font)

        self.ComboBox_SP = QtWidgets.QComboBox(self)
        self.ComboBox_SP.setGeometry(QtCore.QRect(250,50,100,31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.ComboBox_SP.setFont(font)
        self.ComboBox_SP.addItem("Default")

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.Graph = pg.LayoutWidget(self)
        self.Graph.setGeometry(QtCore.QRect(100, 150, 850, 410))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.Graph.setFont(font)
        self.Graph.addWidget(self.canvas)

        self.PB_G = QtWidgets.QPushButton("Get Noise Floor", self)
        self.PB_G.setGeometry(QtCore.QRect(110, 100, 200, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.PB_G.setFont(font)

        self.PB_M = QtWidgets.QPushButton("Measure Noise Floor", self)
        self.PB_M.setGeometry(QtCore.QRect(420,575,200,40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.PB_M.setFont(font)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

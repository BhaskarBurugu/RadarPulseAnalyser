######################################################################################################################
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from pyqtgraph import PlotWidget,plot
import pyqtgraph as pg
from PyQt5.QtWidgets import QHeaderView, QToolBar, QMainWindow, QAction, QMessageBox
######################################################################################################################
class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1900, 980)
        MainWindow.setMaximumSize(1900,980)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
######################################        Creating Table Widget       ############################################
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(50, 485, 850, 410))
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
#######################################       Creating Pushbutton   ###################################################
        self.pushButton_Start = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_Start.setGeometry(QtCore.QRect(860, 905, 180, 51))
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
######################################## Creating Widgets(Plotting Graphs) #############################################
        self.Graph1 = pg.PlotWidget(self.centralwidget)
        self.Graph1.setGeometry(QtCore.QRect(50, 60, 850, 410))
        self.Graph1.setObjectName("Graph1")
        self.Graph1.setLabel('left', 'PRI')
        self.Graph1.setLabel('bottom', 'Pulse Count')

        self.Graph2 = pg.PlotWidget(self.centralwidget)
        self.Graph2.setGeometry(QtCore.QRect(1000, 60, 850, 410))
        self.Graph2.setObjectName("Graph2")
        self.Graph2.setLabel('left', 'AMP')
        self.Graph2.setLabel('bottom', 'TOA')

        self.Graph3 = pg.PlotWidget(self.centralwidget)
        self.Graph3.setGeometry(QtCore.QRect(1000, 485, 850, 410))
        self.Graph3.setObjectName("Graph3")
        self.Graph3.setLabel('left', 'Count')
        self.Graph3.setLabel('bottom', 'TOA')

        ## Set Graph background colour ( White-'w',Black-'k',Green-'g',Red-'r',Yellow-'y',Blue-'b',cyan (bright blue-green)-'c',magenta (bright pink)-'m' ) ###########
        self.Graph1.setBackground('k')
        self.Graph2.setBackground('k')
        self.Graph3.setBackground('k')
        MainWindow.setCentralWidget(self.centralwidget)
############################################## Status Bar  #############################################################
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
##############################################   Tool Bar  #############################################################
        self.toolbar = QtWidgets.QToolBar(MainWindow)
        self.toolbar.setObjectName("toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setGeometry(QtCore.QRect(0,0,1900,50))
        self.toolbar.setIconSize(QtCore.QSize(60,60))
        self.toolbar.addSeparator()
######################################    Creating Tool Bar Icons ######################################################
        self.btn1 = QtWidgets.QAction(MainWindow)
        self.btn1.setIcon(QtGui.QIcon("Exit1.png"))
        self.btn1.setObjectName("btn1")
        self.toolbar.addAction(self.btn1)

        self.btn2 = QtWidgets.QAction(MainWindow)
        self.btn2.setIcon(QtGui.QIcon("Exit1.png"))
        self.btn2.setObjectName("btn2")
        self.toolbar.addAction(self.btn2)

        self.btn3 = QtWidgets.QAction(MainWindow)
        self.btn3.setIcon(QtGui.QIcon("Exit1.png"))
        self.btn3.setObjectName("btn3")
        self.toolbar.addAction(self.btn3)

        self.btn4 = QtWidgets.QAction(MainWindow)
        self.btn4.setIcon(QtGui.QIcon("Exit1.png"))
        self.btn4.setObjectName("btn4")
        self.toolbar.addAction(self.btn4)

        self.pushButton_Start.clicked.connect(self.Plot)

        self.tableWidget.rowCount()

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
########################################################################################################################
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_Start.setText(_translate("MainWindow", "Start PA"))
########################################################################################################################
    def Plot(self):
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]
        pen1 = pg.mkPen(color=(0, 150, 0), width=3, style=QtCore.Qt.SolidLine)
        #pen2 = pg.mkPen(color=(255, 0, 0), width=3, style=QtCore.Qt.SolidLine)
        #pen3 = pg.mkPen(color=(0, 0, 255), width=3, style=QtCore.Qt.SolidLine)
        #pen = pg.mkPen(color=(255, 0, 0))
        self.Graph1.plot(x, y, pen=pen1)
        self.Graph2.plot(x, y, pen=pen1)
        self.Graph3.plot(x, y, pen=pen1)
########################################################################################################################
    def Exit(self):
        reply = QMessageBox.question(self, 'Confirm Exit', 'Are you sure you want to exit Hub Configuration?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            quit()
########################################################################################################################
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
########################################################################################################################
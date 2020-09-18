from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QApplication

from SimulateRadiationPatternDataSet import *

class GenerateStablePRI(QDialog):
    def __init__(self):
        super(GenerateStablePRI, self).__init__()
        self.setWindowTitle("Stable")
        self.resize(500,400)
        self.setMaximumSize(500,400)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.label_Stable = QtWidgets.QLabel("Enter PRI(μs)", self)
        self.label_Stable.setGeometry(QtCore.QRect(100,50,160,31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_Stable.setFont(font)

        self.lineEdit_Stable = QtWidgets.QLineEdit(self)
        self.lineEdit_Stable.setGeometry(QtCore.QRect(280,50,100,31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_Stable.setFont(font)

        self.label_MP = QtWidgets.QLabel("% Missing Pulse", self)
        self.label_MP.setGeometry(QtCore.QRect(100,120,160,31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_MP.setFont(font)

        self.lineEdit_MP = QtWidgets.QComboBox(self)
        self.lineEdit_MP.setGeometry(QtCore.QRect(280, 120, 100, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_MP.setFont(font)
        self.lineEdit_MP.addItems(["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"])

        self.label_ST = QtWidgets.QLabel("Scan Type", self)
        self.label_ST.setGeometry(QtCore.QRect(100, 260, 160, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_ST.setFont(font)

        self.lineEdit_ST = QtWidgets.QComboBox(self)
        self.lineEdit_ST.setGeometry(QtCore.QRect(280, 260, 100, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_ST.setFont(font)
        self.lineEdit_ST.addItems(["Lock On","Circular","Sector Scan"])

        self.label_SR = QtWidgets.QLabel("Gate Way", self)
        self.label_SR.setGeometry(QtCore.QRect(100, 330, 160, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_SR.setFont(font)

        self.lineEdit_SR = QtWidgets.QLineEdit(self)
        self.lineEdit_SR.setGeometry(QtCore.QRect(280, 330, 100, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit_SR.setFont(font)

        self.PB_P = QtWidgets.QPushButton(" Done", self)
        self.PB_P.setGeometry(QtCore.QRect(200, 190, 130, 40))
        self.PB_P.setFont(font)
        self.PB_P.setIcon(QtGui.QIcon("done.png"))
        self.PB_P.setIconSize(QtCore.QSize(20, 20))

        self.trail = False
        self.threat_df =  pd.DataFrame(columns = ['TOA','PW_WIDTH','PW_AMPL'])
        self.Simulate()

    def Simulate(self):
        DWELL_TIME_CONSTANT = 4
        pri = []
        pri.append(1000)


        RPM = 30
        print('@@@@@', RPM)
        Threat_profile = {
                            "Signal Category": "STABLE",
                            "PRI": pri,
                            "Missing Rate": 20,
                            "Scan Type": "Circular",
                            "DOA": -70,
                            "Scan Rate": RPM,  # RPM
                            "Noise Floor": 0  # mV
                        }
        self.threat_df = Genrate_Scan_Pattern_Samples(Threat_profile)
        #Threat_profile['Signal Category']

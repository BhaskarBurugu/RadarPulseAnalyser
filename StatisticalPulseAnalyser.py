#############################################################################################################
import sys
from PyQt5 import QtGui
from PyQt5.QtCore import QRect, QTimer
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QTableWidgetItem, QTableWidget, QToolBar, \
    QHeaderView, QAction
import socket
import selectors
import types
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
#######################################################################################################################
def Plot_DTOA_Hist(DTOA):
    DTOA = [x / 10 for x in DTOA if (x < min(DTOA) * 2) and x > 100]
    Min_PRI = 100  # MIN PRI 100 us
    Max_PRI = 10000  # Max PRI 10msec = 10,000
    if int(min(DTOA) * 0.01) >= 5:
        Bin_Width = 5
    elif int(min(DTOA) * 0.01) <= 0:
        Bin_Width = 1
    else:
        Bin_Width = int(min(DTOA) * 0.01)
    # Bin_Width = 5 if int(min(PRI) * 0.01) >=5 else int(min(PRI) * 0.01)# 2us
    #print('###BIN Width', Bin_Width)
    Number_of_bins = (Max_PRI - Min_PRI) / Bin_Width
   # frq, edges = np.histogram(DTOA, bins=int(Number_of_bins), range=(Min_PRI, Max_PRI))
    frq, edges = np.histogram(DTOA, bins=int(Number_of_bins))
    #frq, edges = np.histogram(x, bins = 2000)
    fig, ax = plt.subplots()
    ax.bar(edges[:-1], frq, width=np.diff(edges), edgecolor="black", align="edge")
    plt.show()
#######################################################################################################################
def Plot_DTOA(DTOA,x_lim2):
    DTOA = np.array([x / 10 for x in DTOA if (x < min(DTOA) * 2) and x > 100])
    if(x_lim2 == 0):
        x_lim2 = 100
    x = [*range(0, DTOA.shape[0], 1)]
   # plt.step(x,DTOA/DTOA.max())
    plt.step(x, DTOA)
    plt.title('DTOA vs Pulse Count')
    plt.ylabel('DTOA (micro sec)')
    plt.xlabel('Pulse Count->')
    plt.xlim(0,x_lim2)
    plt.ylim(DTOA.mean() * 0.70,DTOA.mean()*1.30)
    plt.show()
#######################################################################################################################

#############################################################################################################
def removeOutliers(x, outlierConstant,Low_Th,Upper_Th):
    #a = np.array(x)
    upper_quartile = np.percentile(x, Upper_Th)
    lower_quartile = np.percentile(x, Low_Th)
    IQR = (upper_quartile - lower_quartile) * outlierConstant
    quartileSet = (lower_quartile - IQR, upper_quartile + IQR)
    resultList = []
    drop_list  = []
    for y in x.tolist():
        if y >= quartileSet[0] and y <= quartileSet[1]:
            resultList.append(y)
        else:
            drop_list.append(y)
    return resultList, drop_list
##############################################################################################################
def group(L):
    first = last = L[0]
    for n in L[1:]:
        if n - 1 <= last+2: # Part of the group, bump the end
            last = n
        else: # Not part of the group, yield current group and start a new
            yield first, last
            first = last = n
    yield first, last # Yield the last group
###################################################################################################
def GetPW(PW):
    PW = [x * 10 for x in PW if x>=2000] # convert t0 nsec
    if len(PW) == 0:
        PWStr = '<2us'
        print('PW < 2us')
        return PWStr
   # print(PW)
    Min_PW = 2000   # 2000 ns = 2us max PW is 100us
    Max_PW = 100000
    Bin_Width = 200 # 200ns
    Number_of_bins = (Max_PW - Min_PW) / Bin_Width
    freq, edges = np.histogram(PW, bins=int(Number_of_bins),range = (Min_PW,Max_PW))
    #mode_index = np.argmax(freq)
    #mode_peak = np.max(freq)
    #mode =
   # print (freq)
    #print(edges)

    index = [i for i in range(len(freq)) if freq[i] >= np.max(freq) * 0.3]
  #  print(index)
    group_list = list(group(index))
    #print(group_list)
    PW_List = []
    for count,ele in enumerate(group_list):
        print('Group',count,'LowerPW =',Min_PW + ele[0]*Bin_Width,'END PW=',Min_PW + (ele[1]+1)*Bin_Width)
        PW_List.append((Min_PW + ele[0]*Bin_Width + Min_PW + (ele[1]+1)*Bin_Width)/2)
       # nparray_PW = np.array([x for x in PW if (x >= edges[ele[0]]) and (x < edges[ele[1]+1])])
       # PW_filt, r = removeOutliers(nparray_PW, 1, 25, 75)
       # PW_List.append('{:.2f}'.format(np.mean(PW_filt)))
    print('PW LISt',PW_List)
    #print(PW_List)
    PWStr = ''
    for PW in PW_List:
        #PW_List = [x/1000 for x in PW_List]
        PWStr =  PWStr + '{:.2f}'.format(PW/1000)
    return PWStr
#########################################################################################################
def GetPRI(DTOA):
    DTOA = [x / 10 for x in DTOA if (x < min(DTOA) * 2) and x > 100]  # convert to usec and eliminate hormonics
    # print(PW)
    Min_PRI = 100  # MIN PRI 100 us
    Max_PRI = 10000  # Max PRI 10msec = 10,000
    if int(min(DTOA) * 0.01) >= 5:
        Bin_Width = 5
    elif int(min(DTOA) * 0.01) <= 0:
        Bin_Width = 1
    else:
        Bin_Width = int(min(DTOA) * 0.01)
    # Bin_Width = 5 if int(min(PRI) * 0.01) >=5 else int(min(PRI) * 0.01)# 2us
    #print('###BIN Width', Bin_Width)
    Number_of_bins = (Max_PRI - Min_PRI) / Bin_Width
    freq, edges = np.histogram(DTOA, bins=int(Number_of_bins), range=(Min_PRI, Max_PRI))
    # mode_index = np.argmax(freq)
    # mode_peak = np.max(freq)
    # mode =
    # print (freq)
    # print(edges)
    index = [i for i in range(len(freq)) if freq[i] >= np.max(freq) * 0.3]
    #  print(index)
    group_list = list(group(index))
   # print(group_list)
    PRI_List = []
    for count, ele in enumerate(group_list):
      #  print('Group', count, 'LowerPRI =', Min_PRI + ele[0] * Bin_Width, 'END PRI=',Min_PRI + (ele[1] + 1) * Bin_Width)
       # PRI_List.append((Min_PRI + (ele[0] * Bin_Width) + Min_PRI + (ele[1] + 1) * Bin_Width) / 2)
        nparray_PRI = np.array([x for x in DTOA if (x >= edges[ele[0]]) and (x < edges[ele[1]+1])])
        DTOA_filt, r = removeOutliers(nparray_PRI, 1, 25, 75)
        PRI_List.append('{:.2f}'.format(np.mean(DTOA_filt)))

        #PRI_List.append((edges[ele[0]] + (edges[ele[1] + 1])) / 2)
    # print(PW_List)
    nparray_PRI = np.array(DTOA)
    #print('Std Deviation', np.std(DTOA))
    if len(PRI_List) == 1:
        if np.std(DTOA) < 2.5:
            PRI_Cat = 'STABLE'
           # DTOA_filt,r = removeOutliers(nparray_PRI,1,25,75)
          #  PRI_List[0] = '{:.2f}'.format(np.mean(DTOA_filt))
            #print(np.mean(DTOA_filt))
        else:
            PRI_Cat = 'JITTER'
         #   DTOA_filt, r = removeOutliers(nparray_PRI, 1, 25, 75)
           # PRI_List[0] = '{:.2f}'.format(np.mean(DTOA_filt))
    else:
        PRI_Cat = 'STAGGER LEVEL ' + f'{len(PRI_List)}'
    PRIStr = ''
    for PRI in PRI_List:
        #PW_List = [x/1000 for x in PW_List]
        PRIStr =  PRIStr + f'{PRI}, '
    TrackDataInfo    = {
                        "Signal Category"  :   PRI_Cat,
                        "Pulse Width"      :   '120',
                        "Pulse Amplitude"  :    20,
                        "PRI"              :   PRIStr,#PRI_List,
                      #  'Std Dev'          :   np.std(DTOA),
                        "Scan Type"        :   "Lock-on",
                        "Scan Rate"        :   30,
                        "Min PRI"          :   np.min(DTOA),
                        "Max PRI"          :   np.max(DTOA),
                        "Pulse Count"      :   len(DTOA)
                        }
    return TrackDataInfo
#######################################################################################################################
def Extract_PDW(bytes_array):
    length = int(len(bytes_array)/(4*2))
    PulseWidth = np.empty(length, dtype = 'u4')
    PulseAmpl = np.empty(length, dtype = 'u4')
    DTOA = np.empty(length, dtype = 'u4')

    for i in range(length):
        Lower_Word =  bytes_array[(i*8):(i*8)+4]
        PW_Array = bytes_array[(i*8):(i*8)+2]
        PA_Array = bytes_array[(i*8)+3:(i*8)+4]
      #  print(PW_Array)
        Upper_Word =  bytes_array[(i*8)+4:(i*8)+8]
        PW = int.from_bytes(PW_Array,byteorder='big',signed=False)
        PA = int.from_bytes(PA_Array,byteorder='big',signed=False)
      #  Lower_Word = int.from_bytes(Lower_Word, byteorder='big',signed=False)
        Upper_Word = int.from_bytes(Upper_Word, byteorder='big',signed=False)
        #print(number)
       # print(PW, Lower_Word)
        PulseWidth[i] = PW
        PulseAmpl[i] = PA
        DTOA[i] = Upper_Word
    return PulseWidth, PulseAmpl, DTOA
#################################################################################################################
class MyThread(QThread):
    # Create a counter thread
   # pd_PDW_Update = pyqtSignal(pd.DataFrame)
   # Track_Update = pyqtSignal(dict)
    updatePDW = pyqtSignal(bytes)
    ####################################################################################################################
    ####################################################################################################################
    def __init__(self):
        super().__init__()
        self.StopFlag = False
       # self.StartPulseAnalysis = False
    ####################################################################################################################
    def run(self):
        Ip_info = pd.read_csv("PulseAnalyserConfig.csv")
        IP_PulseAnalyser = Ip_info['IP Addr'][0]
        IP_Gui = Ip_info['IP Addr'][1]
        IP_Server = Ip_info['IP Addr'][2]
        Port_Server = int(Ip_info['Port'][2])
       # print('Pulse Analyser IP is:', IP_PulseAnalyser)
       # print('Gui IP is:', IP_Gui)
       # print('Port Number of Server is:', Port_Server)
        PERFORM_LINKCHECK = b'PerformLinkCheck'
        CAPTURE_PDW = b'CapturePDW'

        START_PULSE_ANALYSIS = b'StartPulseAnalysis'
        PULSEANALYSER = b'PulseAnalyser'
        GUI_CONNECT = b'PAConnectRequest'
        CAPTURE_PDW = b'CapturePDW'
        print("HELLO THIS is Server")
    ###################################################################################################################
        # Load the model in memory
        sel = selectors.DefaultSelector()
        # host = socket.gethostname()
        # IPAddr = socket.gethostbyname(host)
        # print('####',host)
        # print('$$$$',IPAddr)
        GUI_Client_Conn_Status = False
        GUI_IPAddr = ('127.0.0.1', 5410)  # dummy Values
        GUI_Port = 5410  # Dummy Values
        IP_PulseAnalyser = (Ip_info['IP Addr'][0], 5555)
        host = IP_Server  # Standard loopback interface address (localhost)
        port = Port_Server  # Port to listen on (non-privileged ports are > 1023)
        # GUI_IPAddr = host
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((host, port))
        lsock.listen()
        print('listening on', (host, port))
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
    #######################################################################################################################
        def accept_wrapper(sock):
            conn, addr = sock.accept()  # Should be ready to read
            print('accepted connection from', addr)
            conn.setblocking(False)
            data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
            sel.register(conn, events, data=data)
            return conn, addr
    #######################################################################################################################
        def service_connection(key, mask):
            sock = key.fileobj
            data = key.data
            if mask & selectors.EVENT_READ:
                recv_data = sock.recv(5000)  # Should be ready to read old data 1024
                if recv_data:
                    data.inb += recv_data
                   # print('type of recv_data is', data.inb)
                    text = (len(data.inb)).to_bytes(4, byteorder="big", signed=False)
                    sock.send(bytes(text))
                else:
                    print('closing connection to', data.addr)
                    sel.unregister(sock)
                    sock.close()
            if mask & selectors.EVENT_WRITE:
                if data.outb:
                  #  print('echoing', repr(data.outb), 'to', data.addr)
                    sent = sock.send(data.outb)  # Should be ready to write
                    #  print(data.outb)
                    #  print(sent)
                    data.outb = data.outb[sent:]
                #  data.outb = data.outb[1:]
            return data
    #######################################################################################################################
        PulseAnalyser_Client_Conn_Status = False
        Pulse_Analysis_Flag = False
        RAW_DTOA = np.empty(0, dtype='u4')
        PulseWidth = np.empty(0, dtype='u4')
        PulseAmpl = np.empty(0, dtype='u4')
        #######################################################################################################################
        while True:
            if self.StartPulseAnalysis == False:
                RAW_DTOA = np.empty(0, dtype='u4')
                PulseWidth = np.empty(0, dtype='u4')
                PulseAmpl = np.empty(0, dtype='u4')
            try:
                events = sel.select(timeout=1)
            except:
                print("error")
            # events = sel.select(timeout=None)
            for key, mask in events:
                try:
                    if key.data is None:
                        conn, addr1 = accept_wrapper(key.fileobj)
                    else:
                        sock = key.fileobj
                        data = key.data
                        # data = service_connection(key, mask)
                        if mask & selectors.EVENT_READ:
                            recv_data = sock.recv(5000)  # Should be ready to read 5000
                            if recv_data:
                                data.inb = recv_data
                                CmdByte = recv_data[0]
                                GUI_Client_Conn_Status = True
                                if (GUI_Client_Conn_Status == True) and (recv_data != GUI_CONNECT):
                                #if (1):
                                    # print('GUI Connected Data Received from Pulse Analyser')
                                    if (recv_data[0] == 240):  # PDWs Start of Byte
                                        # if(CmdByte == b'\xf0'):   #PDWs Start of Byte
                                        if (self.StartPulseAnalysis == True):
                                            self.updatePDW.emit(recv_data)
                                           # print('TYPE',type(recv_data))
                                else:
                                    print('######  GUI Link Down  #######\n')
                                if (recv_data == PULSEANALYSER):
                                    IP_PulseAnalyser = data.addr
                                    sock_pulse_analyser = sock
                                    # addr_pulse_analyser = key.data.addr
                                    PulseAnalyser_Client_Conn_Status = True
                                    print('Pulse Analyser Connected', IP_PulseAnalyser)
                                    ###### Pulse Analysis Command to be sent to Pulse Analyser
                                    # sock_pulse_analyser.send(b'Start Pulse Analysis Command Received\n\r')
                                if (recv_data == CAPTURE_PDW):
                                    print('Capture PDW Command')
                                    sock_pulse_analyser.send(b'Capture PDW Command Received\n\r')
                                    # text =  (len(data.inb)).to_bytes(4, byteorder="big", signed=False)
                                    # sock.send(bytes(text))
                            else:
                                print('closing connection to', data.addr)
                                if (data.addr == IP_PulseAnalyser):
                                    PulseAnalyser_Client_Conn_Status = False
                                    Pulse_Analysis_Flag = False
                                    print('PulseAnalyser_Client_Conn_Status', PulseAnalyser_Client_Conn_Status)
                                sel.unregister(sock)
                                sock.close()
                except:
                    print('If Error')
                    print(key.fileobj)
                    s1 = key.fileobj
                    sel.unregister(s1)
                    s1.close()
                    print('Socket Closed')
                # ('closing Socket')
        sel.unregister(lsock)
        lsock.close()
########################################################################################################################
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.Title_list = ["PW", " PA ", "Signal\nCategory", "PRI", "PRI \n Min", "PRI \n Max", "Scan \n Type", "Scan \n Rate"]
        title = "Radar Pulse Analyser"
        left = 500
        top = 300
        width = 800
        height = 600
        iconName = "icon.png"
        self.ServerStopFlag = False
        self.ClearDispCount = 0
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(iconName))
        self.setGeometry(left,  top, width, height)
        self.UiComponents()
        self.show()
      #  self.Text.append("Server Started")
        self.Server_Start()

    ###################################################################################################################
    def UiComponents(self):
        self.toolbar = QToolBar(self)
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("background-color : white")
        self.toolbar.setGeometry(QRect(0,0,800,60))
        self.Text = QTextEdit(self)
        self.Text.move(0, 500)
        self.Text.resize(800, 100)
        self.button = QPushButton("Start Pulse Analysis", self)
        self.button.move(150,150)
        self.button.setGeometry(QRect(10,455,180,40))
        self.button1 = QPushButton("Stop Pulse Analysis",self)
        self.button1.move(40,40)
        self.button1.setGeometry(QRect(200,455,180,40))
        self.button2 = QPushButton("Clear",self)
        self.button2.move(50,50)
        self.button2.setGeometry(QRect(390,455,180,40))
        self.button3 = QPushButton("Save PDW",self)
        self.button3.setGeometry(QRect(580,455,180,40))
        self.ActplotDTOA = QAction("PLSCMT\nVS\nDTOA",self)
        self.ActplotHistPRI = QAction("Histogram",self)
        self.ActplotHistPW = QAction("PA\nVS\nDTOA",self)
        self.toolbar.addAction(self.ActplotDTOA)
        self.toolbar.addAction(self.ActplotHistPRI)
        self.toolbar.addAction(self.ActplotHistPW)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(QRect(10, 60, 775, 380))
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(9)
        font.setItalic(True)
        font.setWeight(75)
        self.tableWidget.setFont(font)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(8)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setHorizontalHeaderLabels(self.Title_list)

        self.button.clicked.connect(self.Server_Start)
        self.button1.clicked.connect(self.Server_Stop)
        self.button2.clicked.connect(self.Clear)
        self.button3.clicked.connect(self.savePDW)

        self.ActplotDTOA.triggered.connect(self.plotDTOA)
        self.ActplotHistPRI.triggered.connect(self.plotHistPRI)
        self.ActplotHistPW.triggered.connect(self.plotHistPW)

        self.button.setEnabled(False)
        self.CurRowInd = 0
        self.thread = MyThread()
       # self.thread.change_value.connect(self.setProgressVal)
        self.thread.StopFlag = False
        self.thread.start()
        self.thread.StartPulseAnalysis = False
       # self.thread.pd_PDW_Update.connect(self.updateGraphs)
       # self.thread.Track_Update.connect(self.updateTrackTable)
        self.thread.updatePDW.connect(self.ExtractPDW)
        self.RAW_DTOA = np.empty(0, dtype='u4')
        self.PulseWidth = np.empty(0, dtype='u4')
        self.PulseAmpl = np.empty(0, dtype='u4')
        self.PDWUpdateFlag = False
        self.timer = QTimer(self)
        #self.timer = 2000
       # self.timer.timeout(2000)
        self.timer.timeout.connect(self.ExtractPulseParam)
        ############################################################################################################

    def plotDTOA(self):
        if self.SignalType == 'JITTER' :
            Plot_DTOA(self.RAW_DTOA,x_lim2=500)
        else :
            Plot_DTOA(self.RAW_DTOA, x_lim2=100)

    def plotHistPRI(self):
        Plot_DTOA_Hist(self.RAW_DTOA)

    def plotHistPW(self):
        Plot_DTOA_Hist(self.PulseWidth)

    def ExtractPDW(self,recv_data):
       # self.Text.append('Extract PDW')
        PW, PA, D_TOA = Extract_PDW(recv_data[1:])
        self.RAW_DTOA = np.concatenate((self.RAW_DTOA, D_TOA), axis=0)
        self.PulseWidth = np.concatenate((self.PulseWidth, PW), axis=0)
        self.PulseAmpl = np.concatenate((self.PulseAmpl, PA), axis=0)
        self.PDWUpdateFlag = True
#####################################################################################################################
    def ExtractPulseParam(self):
        self.Text.append('Pulse Count'+ str(len(self.RAW_DTOA)))
       # self.CurRowInd = self.tableWidget.rowCount()
       # self.tableWidget.setRowCount(self.CurRowInd+1)
        if self.PDWUpdateFlag == True:
            try:
                self.tableWidget.setRowCount(self.CurRowInd + 1)
               # self.CurRowInd = 1
                if len(self.RAW_DTOA > 1000):
                    TrackData = GetPRI(self.RAW_DTOA[-1000:])
                    TrackData['Pulse Width'] = GetPW(self.PulseWidth[-1000:])
                else:
                    TrackData = GetPRI(self.RAW_DTOA)
                    TrackData['Pulse Width'] = GetPW(self.PulseWidth)
                print(TrackData)
                self.SignalType =TrackData.get('Signal Category')
                self.Text.clear()
                self.Text.append(str(TrackData))
                PW = f'''{TrackData['Pulse Width']}'''
                PA = f'''{TrackData['Pulse Amplitude']}'''
                PRI = f'''{TrackData['PRI']}'''
                minPRI = f'''{TrackData['Min PRI']}'''
                maxPRI = f'''{TrackData['Max PRI']}'''
                ScanRate = f'''{TrackData['Scan Rate']}'''
                self.tableWidget.setItem(self.CurRowInd, 0, QTableWidgetItem(PW))
                self.tableWidget.setItem(self.CurRowInd, 1, QTableWidgetItem(PA))
                self.tableWidget.setItem(self.CurRowInd, 2, QTableWidgetItem(TrackData.get('Signal Category')))
                self.tableWidget.setItem(self.CurRowInd, 3, QTableWidgetItem(PRI))
                self.tableWidget.setItem(self.CurRowInd, 4, QTableWidgetItem(minPRI))
                self.tableWidget.setItem(self.CurRowInd, 5, QTableWidgetItem(maxPRI))
                self.tableWidget.setItem(self.CurRowInd, 6, QTableWidgetItem(TrackData.get('Scan Type')))
                self.tableWidget.setItem(self.CurRowInd, 7, QTableWidgetItem(ScanRate))
                #  print (GetPW(PulseWidth))
                #self.Track_Update.emit(TrackData)
            except:
                self.Text.append('No PDWs in Buffer')
            self.PDWUpdateFlag = False
        self.timer.start(2000)
        #Munny Write here to insert into table TrackData
        #self.savePDW()
####################################################################################################################
    def savePDW(self):
        TOA = []
        TOA.append(0)
        for i in range(1, len(self.RAW_DTOA)):
            TOA.append(TOA[i - 1] + self.RAW_DTOA[i - 1])
        pdwdata = []
        # for i in range(1000):
        #     pdwdata.append([PulseWidth[i], PulseAmpl[i], RAW_DTOA[i], TOA[i]])
        try:
            df = pd.DataFrame(columns=['TOA', 'PW', 'PA', 'DTOA'])
            df['PW'] = self.PulseWidth
            df['PA'] = self.PulseAmpl
            df['DTOA'] = self.RAW_DTOA
            df['TOA'] = TOA
            df.to_csv('pdw.csv')
           # self.pd_PDW_Update.emit(df)
        except:
            print('Error')

    ###################################################################################################################
    def Server_Start(self):
        self.Clear()
        self.Text.append("Pulse Analysis Started")
        self.RAW_DTOA = np.empty(0, dtype='u4')
        self.PulseWidth = np.empty(0, dtype='u4')
        self.PulseAmpl = np.empty(0, dtype='u4')

        self.button.setEnabled(False)
        self.button1.setEnabled(True)
       # self.Text.append("Server Started")
        self.thread.StartPulseAnalysis = True
        self.timer.start(2000)
    ###################################################################################################################
    def Server_Stop(self):
       # self.thread.StopFlag = True
        self.button.setEnabled(True)
        self.button1.setEnabled(False)
        self.Text.append("Pulse Analysis Stopped")
        self.thread.StartPulseAnalysis = False
        #self.thread.exit()
       #self.ServerStopFlag = True
        self.timer.stop()
    ###################################################################################################################
    def updateGraphs(self, df_Pdw):
        print('Update Graphs')
       # print(df_Pdw.head())
        # Munny write here for Graphs updation

    def updateTrackTable(self, TrackData):
        print('Update Table')
        print(TrackData)
        # Munny Write here for Tbale updation
#######################################################################################################################
    def Clear(self):
        self.Text.clear()
#######################################################################################################################
if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = Window()
    try:
        sys.exit(App.exec())
    except:
        print("ERRRRR")
####################################################################################################################
#############################################################################################################
import sys
from PyQt5 import QtGui
from PyQt5.QtCore import QRect
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton,QTextEdit
import socket
import selectors
import types
import numpy as np
import pandas as pd
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
    PW = [x * 10 for x in PW] # convert t0 nsec
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
   # print(group_list)
    PW_List = []
    for count,ele in enumerate(group_list):
        print('Group',count,'LowerPW =',Min_PW + ele[0]*Bin_Width,'END PW=',Min_PW + (ele[1]+1)*Bin_Width)
        PW_List.append((Min_PW + ele[0]*Bin_Width + Min_PW + (ele[1]+1)*Bin_Width)/2)
       # nparray_PW = np.array([x for x in PW if (x >= edges[ele[0]]) and (x < edges[ele[1]+1])])
       # PW_filt, r = removeOutliers(nparray_PW, 1, 25, 75)
       # PW_List.append('{:.2f}'.format(np.mean(PW_filt)))

    #print(PW_List)
    PW_List = [x/1000 for x in PW_List]
    return PW_List
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

    TrackDataInfo    = {
                        "Signal Category"  :   PRI_Cat,
                        "Pulse Width"      :   [2],
                        "Pulse Amplitude"  :    20,
                        "PRI"              :   PRI_List,
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
    pd_PDW_Update = pyqtSignal(pd.DataFrame)
    Track_Update = pyqtSignal(dict)
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
                                            # print('Length of PDWs',int(len(recv_data)/(4*2)))
                                            PW, PA, D_TOA = Extract_PDW(recv_data[1:])
                                            RAW_DTOA = np.concatenate((RAW_DTOA, D_TOA), axis=0)
                                            PulseWidth = np.concatenate((PulseWidth, PW), axis=0)
                                            PulseAmpl = np.concatenate((PulseAmpl, PA), axis=0)
                                           # TrackData = GetPRI(RAW_DTOA)
                                          #  print (GetPW(PulseWidth))
                                          #  self.Track_Update.emit(TrackData)
                                            TOA = []
                                            TOA.append(0)
                                            for i in range(1, len(RAW_DTOA)):
                                                TOA.append(TOA[i - 1] + RAW_DTOA[i - 1])
                                            pdwdata = []
                                           # for i in range(1000):
                                           #     pdwdata.append([PulseWidth[i], PulseAmpl[i], RAW_DTOA[i], TOA[i]])
                                            try:
                                                df = pd.DataFrame(columns=['TOA','PW', 'PA', 'DTOA'])
                                                df['PW']    = PulseWidth
                                                df['PA']    = PulseAmpl
                                                df['DTOA']  = RAW_DTOA
                                                df['TOA']  = TOA
                                            #    df.to_csv('pdw.csv')
                                                self.pd_PDW_Update.emit(df)
                                            except:
                                                print('Error')
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
        title = "Multi-Vibration Sensor Server- Version B0.2"
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
        self.Text = QTextEdit(self)
        self.Text.move(0, 0)
        self.Text.resize(800, 500)
        self.button = QPushButton("Start Server", self)
        self.button.move(150,150)
        self.button.setGeometry(QRect(50,525,200,40))
        self.button1 = QPushButton("Stop Server",self)
        self.button1.move(40,40)
        self.button1.setGeometry(QRect(280,525,200,40))
        self.button2 = QPushButton("Clear",self)
        self.button2.move(50,50)
        self.button2.setGeometry(QRect(510,525,200,40))
        self.button.clicked.connect(self.Server_Start)
        self.button1.clicked.connect(self.Server_Stop)
        self.button2.clicked.connect(self.Clear)
        self.button.setEnabled(False)
        self.thread = MyThread()
       # self.thread.change_value.connect(self.setProgressVal)
        self.thread.StopFlag = False
        self.thread.start()
        self.thread.StartPulseAnalysis = False
        self.thread.pd_PDW_Update.connect(self.updateGraphs)
        self.thread.Track_Update.connect(self.updateTrackTable)

    ###################################################################################################################
    def Server_Start(self):
        self.Text.append("Pulse Analysis Started")
        self.button.setEnabled(False)
        self.button1.setEnabled(True)
       # self.Text.append("Server Started")
        self.thread.StartPulseAnalysis = True
    ###################################################################################################################
    def Server_Stop(self):
       # self.thread.StopFlag = True
        self.button.setEnabled(True)
        self.button1.setEnabled(False)
        self.Text.append("Pulse Analysis Stopped")
        self.thread.StartPulseAnalysis = False
        #self.thread.exit()
       #self.ServerStopFlag = True
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
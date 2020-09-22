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
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
#######################################################################################################################
def Plot_DTOA_Hist(x):
    frq, edges = np.histogram(x, bins = 2000)
    fig, ax = plt.subplots()
    ax.bar(edges[:-1], frq, width=np.diff(edges), edgecolor="black", align="edge")
    plt.show()
#######################################################################################################################
def Plot_DTOA(DTOA,x_lim2):
    if(x_lim2 == 0):
        x_lim2 = 100
    x = [*range(0, DTOA.shape[0], 1)]
   # plt.step(x,DTOA/DTOA.max())
    plt.step(x, DTOA)
    plt.title('DTOA vs Pulse Count')
    plt.ylabel('DTOA (micro sec)')
    plt.xlabel('Pulse Count->')
    plt.xlim(0,x_lim2)
    plt.ylim(DTOA.min() * 0.8,DTOA.max()*1.2)
    plt.show()
#######################################################################################################################
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
#######################################################################################################################
def Get_StaggerPRI_from_Cluster(x,no_of_clusters):
    # create kmeans object
    DataSet_for_Cluster = np.expand_dims(x,axis = 1)
    DataSet_for_Cluster.shape
    kmeans = KMeans(n_clusters=no_of_clusters)
    kmeans.fit(DataSet_for_Cluster)
    pri = kmeans.cluster_centers_
    pri = pri.flatten()
    pri.sort()
    return pri
#######################################################################################################################
def ClassifyPRI(model, DTOA):
    Target_Category = {
                        'Constant_PRI'         : 0,
                        'Jittered_PRI'         : 1,
                        'StaggeredPRI'         : 2,
                      }
    Category = [
                'Constant_PRI',
                'Jittered_PRI',
                'StaggeredPRI_Level_2',
                'StaggeredPRI_Level_3',
                'StaggeredPRI_Level_4',
                'StaggeredPRI_Level_5',
                'StaggeredPRI_Level_6',
                'StaggeredPRI_Level_7',
                'StaggeredPRI_Level_8'
                ]
    TrackDataInfo    = {
                        "Signal Category"  :   "STABLE",
                        "Pulse Width"      :   [2],
                        "PRI"              : [123],
                        "Scan Type"        : "Lock-on",
                        "Scan Rate"        : 30,
                        "Min PRI"          : 123,
                        "Max PRI"          : 124
                        }
    dataset = DTOA/10
    dataset = np.expand_dims(dataset, axis=0)
    dataset = np.expand_dims(dataset, axis=0)
   # dataset = dataset
    y_pred_ohe = model.predict(dataset)
    print('Clasification Quality',np.max(y_pred_ohe[0])*100)
    Signal_Category = np.argmax(y_pred_ohe[0])
  #  print('Signal Category is',Category[Signal_Category])
   # y = np.delete(y_pred_ohe[0],np.argmax(y_pred_ohe[0]))
  #  print('@@@@@@@',y_pred_ohe[0])
  #  print('##########',np.max(y))

   # y = [x for x in y_pred_ohe[0] if y_pred_ohe[0] > 0.3]
  #  print('second####',y)
    #Track_Length = 5
    TrackData = bytearray(0)
    TrackData = b'\xF5'
    if(Signal_Category == 0):  # Constant PRI
        DTOA_Filt,r = removeOutliers(DTOA, 1, 25, 75)
        DTOA_np = np.array(DTOA_Filt,dtype= '>u4')
        PRI = "{:.2f}".format(DTOA_np.mean()/10)
        #TrackData = TrackData + (Target_Category['Constant_PRI']).to_bytes(1, byteorder='big')
        #TrackData = TrackData + PRI.tobytes()
      #  print('Constant_PRI(us)',PRI/1000)
        TrackDataInfo['Signal Category'] = 'STABLE'
        TrackDataInfo['PRI'][0] = PRI
    elif (Signal_Category == 1):  # Jittered PRI
        print('###JITTER####')
        DTOA_Filt, r = removeOutliers(DTOA, 1, 25, 75)
        DTOA_np = np.array(DTOA_Filt,dtype= '>u4')
        PRI = "{:.2f}".format(DTOA_np.mean()/10)
        PRI_min = "{:.2f}".format(DTOA_np.min()/10)
        PRI_max = "{:.2f}".format(DTOA_np.max()/10)
      #  print('Jittered_PRI(us)',PRI/1000)
     #   print('Min PRI(us)',PRI_min/1000)
      #  print('Max PRI(us)',PRI_max/1000)
       # TrackData = TrackData + (Target_Category['Jittered_PRI']).to_bytes(1, byteorder='big')
      #  TrackData = TrackData + PRI.tobytes()
      #  TrackData = TrackData + PRI_min.tobytes()
      #  TrackData = TrackData + PRI_max.tobytes()


        TrackDataInfo['Signal Category'] = 'JITTER'
        TrackDataInfo['PRI'][0] = PRI
        TrackDataInfo['Min PRI'] = PRI_min
        TrackDataInfo['Max PRI'] = PRI_max

    else :     # Staggered PRI
       # print('Staggered PRI')
        Stag_PRI = Get_StaggerPRI_from_Cluster(DTOA,np.argmax(y_pred_ohe[0]))
     #   TrackData = TrackData + (Target_Category['StaggeredPRI']).to_bytes(1, byteorder='big')
    #    for PRI in Stag_PRI:
     #       print("Staggger PRI",round(PRI,2))
      #      PRI = np.array(PRI*1000,dtype= '>u4')
      #      TrackData = TrackData + PRI.tobytes()

        TrackDataInfo['Signal Category'] = Category[Signal_Category] #'STAGGER'
        TrackDataInfo['PRI'] = ["{:.2f}".format(x/10) for x in Stag_PRI]

   # print(DTOA[0:10])
  #  Plot_DTOA(DTOA,100)
 #   Plot_DTOA_Hist(DTOA)
    return TrackDataInfo
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
        model = tf.keras.models.load_model('pulseanalyser_1000_01_09_20.h5')
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

                                            if (RAW_DTOA.shape[0] >= 300):
                                                # RAW_DTOA = np.empty(TOA.shape[0]-1)
                                                # RAW_DTOA = TOA
                                                DTOA, xx = removeOutliers(RAW_DTOA, 1, 15, 85)
                                                if (len(DTOA) > 1000):
                                                    DataSet = np.array(DTOA[0:1000], dtype='u4')
                                                    TrackData = ClassifyPRI(model, DataSet)

                                                  #  print(TrackData)
                                                   # GUI_sock.send(TrackData)
                                                    self.Track_Update.emit(TrackData)
                                                    # TOA = np.empty(0,dtype='u4')
                                                    TOA = []
                                                    TOA.append(0)
                                                    for i in range(1, 1000):
                                                        TOA.append(TOA[i - 1] + DTOA[i - 1])

                                                  #  print(len(PulseWidth), PulseAmpl)
                                                  #  print(len(PulseWidth), PulseWidth)
                                                 #   print(len(RAW_DTOA))
                                                    pdwdata = []
                                                    for i in range(1000):
                                                        pdwdata.append([PulseWidth[i], PulseAmpl[i], DTOA[i], TOA[i]])
                                                    # data1 = np.array([PulseWidth[0:1000],PulseAmpl[0:1000],RAW_DTOA[0:1000]])
                                                    # print(pdwdata)
                                                    try:
                                                        df = pd.DataFrame(data=pdwdata,
                                                                          columns=['PW', 'PA', 'DTOA', 'TOA'])
                                                        # df['PW1'] = PulseWidth
                                                        # df = pd.DataFrame(data1,columns=['PW', 'PA', 'DTOA'])
                                                        #print(df)
                                                        df.to_csv('pdw.csv')
                                                        self.pd_PDW_Update.emit(df)
                                                    except:
                                                        print('Error')
                                                    # df['PW'] = list(PulseWidth)
                                                    # print(df)
                                                    #   df['PA'] = PulseAmpl
                                                    #  df['DTOA'] = RAW_DTOA
                                                    #   print(df.head())
                                                    #    df['TOA'] = TOA
                                                    #  df.to_csv('pdw.csv')

                                                    # print(len(TOA))

                                                   # print('###TRACK DATA TYPE#####\n', type(TrackData))
                                                    RAW_DTOA = np.empty(0, dtype='u4')

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

        self.thread.pd_PDW_Update.connect(self.setProgressVal)
        self.thread.StopFlag = False
        self.thread.start()
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
    def setProgressVal(self, val):
        if(self.ClearDispCount >10):
            self.ClearDispCount = 0
            self.Text.clear()
            self.Text.setText(val)
        else:
            self.Text.append(val)
        self.ClearDispCount = self.ClearDispCount + 1
        #self.Text.setText(val)
       # print(val)
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
########################################################################################################################
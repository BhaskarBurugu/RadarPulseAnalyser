#######################################################################################################################
import socket
import selectors
import types
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
#######################################################################################################################
Ip_info = pd.read_csv("PulseAnalyserConfig.csv")
IP_PulseAnalyser = Ip_info['IP Addr'][0]
IP_Gui = Ip_info['IP Addr'][1]
IP_Server = Ip_info['IP Addr'][2]
Port_Server = int(Ip_info['Port'][2])
print('Pulse Analyser IP is:',IP_PulseAnalyser)
print('Gui IP is:',IP_Gui)
print('Port Number of Server is:',Port_Server)
PERFORM_LINKCHECK = b'PerformLinkCheck'
CAPTURE_PDW       = b'CapturePDW'
START_PULSE_ANALYSIS = b'StartPulseAnalysis'
PULSEANALYSER        = b'PulseAnalyser'
GUI_CONNECT          = b'PAConnectRequest'
CAPTURE_PDW          = b'CapturePDW'
print("HELLO THIS is Server")
#######################################################################################################################
def Bytes_to_int32(bytes_array):
    length = int(len(bytes_array))
    number_list = np.empty(1000)
    for i in range(1000):
        bytearr =  bytes_array[(i*4):(i*4)+4]
        number = int.from_bytes(bytearr, byteorder='little')
        #print(number)
        number_list[i] = number
    return number_list   
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
Category = {
            'Constant_PRI'       ,
            'Jittered_PRI'       , 
            'StaggeredPRI_Level_2',
            'StaggeredPRI_Level_3',
            'StaggeredPRI_Level_4',
            'StaggeredPRI_Level_5',
            'StaggeredPRI_Level_6',
            'StaggeredPRI_Level_7', 
            'StaggeredPRI_Level_8'
            }
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
    #dataset = np.array(df)
  #  dataset = DTOA
  #  DTOA = DTOA / 10

    dataset = DTOA
    dataset = np.expand_dims(dataset, axis=0)  
    dataset = np.expand_dims(dataset, axis=0)  
    dataset = dataset
    y_pred_ohe = model.predict(dataset)
    print('Clasification Quality',np.max(y_pred_ohe[0])*100)
    Signal_Category = np.argmax(y_pred_ohe[0])
    print('Signal Category is',Category[Signal_Category])
    y = np.delete(y_pred_ohe[0],np.argmax(y_pred_ohe[0]))
    print('@@@@@@@',y_pred_ohe[0])
    print('##########',np.max(y))

   # y = [x for x in y_pred_ohe[0] if y_pred_ohe[0] > 0.3]
  #  print('second####',y)
    #Track_Length = 5
    TrackData = bytearray(0)  
    TrackData = b'\xF5'
    if(Signal_Category == 0):  # Constant PRI
        PRI = np.array(DTOA.mean()*1000,dtype= '>u4')
        TrackData = TrackData + (Target_Category['Constant_PRI']).to_bytes(1, byteorder='big')    
        TrackData = TrackData + PRI.tobytes()
        print('Constant_PRI(us)',PRI/1000)        
    elif (Signal_Category == 1):  # Jittered PRI
        PRI = np.array(DTOA.mean()*1000,dtype= '>u4')
        PRI_min = np.array(DTOA.min()*1000,dtype= '>u4')
        PRI_max = np.array(DTOA.max()*1000,dtype= '>u4')
        print('Jittered_PRI(us)',PRI/1000)
        print('Min PRI(us)',PRI_min/1000)
        print('Max PRI(us)',PRI_max/1000)
        TrackData = TrackData + (Target_Category['Jittered_PRI']).to_bytes(1, byteorder='big')    
        TrackData = TrackData + PRI.tobytes()
        TrackData = TrackData + PRI_min.tobytes()
        TrackData = TrackData + PRI_max.tobytes()
    else :     # Staggered PRI
        print('Staggered PRI')
        Stag_PRI = Get_StaggerPRI_from_Cluster(DTOA,np.argmax(y_pred_ohe[0]))
        TrackData = TrackData + (Target_Category['StaggeredPRI']).to_bytes(1, byteorder='big') 
        for PRI in Stag_PRI:
            print("Staggger PRI",round(PRI,2))
            PRI = np.array(PRI*1000,dtype= '>u4')            
            TrackData = TrackData + PRI.tobytes()
    print(DTOA[0:10])
    Plot_DTOA(DTOA,100)
    Plot_DTOA_Hist(DTOA)
    return TrackData
#######################################################################################################################
def Plot_DTOA_Hist(x):
    frq, edges = np.histogram(x, bins = 2000)
    fig, ax = plt.subplots()
    ax.bar(edges[:-1], frq, width=np.diff(edges), edgecolor="black", align="edge")
    plt.show()
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
def Extract_PDW(bytes_array):
    length = int(len(bytes_array)/(4*2))
    PDW1 = np.empty(length, dtype = 'u4')
    PDW2 = np.empty(length, dtype = 'u4')
    for i in range(length):
        Lower_Word =  bytes_array[(i*8):(i*8)+4]
        Upper_Word =  bytes_array[(i*8)+4:(i*8)+8]
        Lower_Word = int.from_bytes(Lower_Word, byteorder='big',signed=False)
        Upper_Word = int.from_bytes(Upper_Word, byteorder='big',signed=False)
        #print(number)
        PDW1[i] = Lower_Word
        PDW2[i] = Upper_Word
    return PDW1, PDW2    
#######################################################################################################################
#Load the model in memory
model = tf.keras.models.load_model('pulseanalyser_1000_01_09_20.h5')
sel = selectors.DefaultSelector()
#host = socket.gethostname()
#IPAddr = socket.gethostbyname(host)
#print('####',host)
#print('$$$$',IPAddr)
GUI_Client_Conn_Status = False
GUI_IPAddr = ('127.0.0.1', 5410)  # dummy Values
GUI_Port = 5410  # Dummy Values
IP_PulseAnalyser = (Ip_info['IP Addr'][0],5555)
host =  IP_Server # Standard loopback interface address (localhost)
port = Port_Server        # Port to listen on (non-privileged ports are > 1023)
#GUI_IPAddr = host
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print('listening on', (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)
events = selectors.EVENT_READ | selectors.EVENT_WRITE
#######################################################################################################################
def accept_wrapper(sock):
    conn, addr = sock.accept()  #Should be ready to read
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
        if recv_data :
            data.inb += recv_data
            print('type of recv_data is',data.inb)
            text =  (len(data.inb)).to_bytes(4, byteorder="big", signed=False)
            sock.send(bytes(text))
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
          #  print(data.outb)
          #  print(sent)
            data.outb = data.outb[sent:]
          #  data.outb = data.outb[1:] 
    return data
#######################################################################################################################
PulseAnalyser_Client_Conn_Status = False
GUI_Client_Conn_Status = False
Pulse_Analysis_Flag = False
#######################################################################################################################
while True:
    try:
        events = sel.select(timeout=1)
    except:
        print("error")
    #events = sel.select(timeout=None)
    for key, mask in events:
        try:
            if key.data is None:
                conn, addr1 = accept_wrapper(key.fileobj)
            else:
                sock = key.fileobj
                data = key.data
                #data = service_connection(key, mask)
                if mask & selectors.EVENT_READ:
                        recv_data = sock.recv(5000)  # Should be ready to read 5000
                        if recv_data :
                            data.inb = recv_data
                            CmdByte = recv_data[0]

                            if (GUI_Client_Conn_Status == True) and (recv_data != GUI_CONNECT):
                               # print('GUI Connected Data Received from Pulse Analyser')
                                if(recv_data[0] == 240):   #PDWs Start of Byte
                                    #if(CmdByte == b'\xf0'):   #PDWs Start of Byte
                                    if(Pulse_Analysis_Flag == True):
                                        #print('Length of PDWs',int(len(recv_data)/(4*2)))
                                        PDW1, PDW2 = Extract_PDW(recv_data[1:])
                                        TOA = np.concatenate((TOA,PDW2),axis = 0)
                                        if(TOA.shape[0] >= 300):
                                            RAW_DTOA = np.empty(TOA.shape[0]-1)
                                            RAW_DTOA = TOA
                                            DTOA, xx = removeOutliers(RAW_DTOA,1,15,85)

                                            if(len(DTOA) > 1000):
                                                DataSet = np.array(DTOA[0:1000], dtype = 'u4')
                                                TrackData = ClassifyPRI(model,DataSet)
                                                GUI_sock.send(TrackData)
                                                print('PRI Category is',TrackData)
                                                TOA = np.empty(0,dtype = 'u4')
                            else:
                                print('######  GUI Link Down  #######\n')

                            if (recv_data == PULSEANALYSER):
                                IP_PulseAnalyser = data.addr
                                sock_pulse_analyser = sock
                                #addr_pulse_analyser = key.data.addr
                                PulseAnalyser_Client_Conn_Status = True
                                print('Pulse Analyser Connected',IP_PulseAnalyser)

                            if (recv_data == GUI_CONNECT):
                                if ((GUI_Client_Conn_Status == False) or (data.addr == GUI_IPAddr)):
                                    GUI_IPAddr = data.addr
                                    GUI_sock = sock
                                    GUI_Client_Conn_Status = True
                                    print('GUI Connected',GUI_IPAddr)
                                    if(PulseAnalyser_Client_Conn_Status == True):
                                        GUI_sock.send(b'Connection Established with Pulse Analyser\n\r')
                                    else :
                                        GUI_sock.send(b'Connection with Pulse Analyser Failed\n\r')
                                else:
                                    sel.unregister(sock)
                                    sock.close()

                            if (recv_data == START_PULSE_ANALYSIS):
                                print('Pulse Analysis Command')
                                Pulse_Analysis_Flag = True
                                TOA = np.empty(0,dtype = 'u4')
                                ###### Pulse Analysis Command to be sent to Pulse Analyser
                                #sock_pulse_analyser.send(b'Start Pulse Analysis Command Received\n\r')
                            if (recv_data == CAPTURE_PDW):
                                print('Capture PDW Command')
                                sock_pulse_analyser.send(b'Capture PDW Command Received\n\r')
                                #text =  (len(data.inb)).to_bytes(4, byteorder="big", signed=False)
                                #sock.send(bytes(text))
                        else:
                            print('closing connection to', data.addr)
                            if(data.addr == IP_PulseAnalyser):
                                PulseAnalyser_Client_Conn_Status = False
                                Pulse_Analysis_Flag = False
                                print('PulseAnalyser_Client_Conn_Status',PulseAnalyser_Client_Conn_Status)
                            elif (data.addr == GUI_IPAddr):
                                GUI_Client_Conn_Status = False
                                Pulse_Analysis_Flag = False
                                print('GUI_Client_Conn_Status',GUI_Client_Conn_Status)
                            sel.unregister(sock)
                            sock.close()

        except:
            print('If Error')
            print(key.fileobj)
            s1 = key.fileobj
            sel.unregister(s1)
            s1.close()
            print('Socket Closed')
        #('closing Socket')
sel.unregister(lsock)
lsock.close()
#######################################################################################################################
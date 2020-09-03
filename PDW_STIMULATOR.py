########################################################################################################################
from PyQt5 import QtCore
from PyQt5 import QtWidgets
import sys
import socket
import numpy as np
from random import randint
import random
from tqdm import tqdm
import time
########################################################################################################################
def Generate_DTOA(TOA):
    RAW_DTOA = []
    #print('%%%%',len(TOA))
    for i in range(0, len(TOA)-1):
        RAW_DTOA.append(TOA[i + 1] - TOA[i])
   # print('####',len(RAW_DTOA))
  #  print(RAW_DTOA)
    return RAW_DTOA
########################################################################################################################
def Generate_Constant_PRI(pri):
    # Value to be entered in the range of 0 to 1 i.e 0, 0.1, 0.2, 0.3 etc
    # pri = pri
    Noise_Std_Deviation = random.uniform(0.0, 0.9)
    print('Standard Deviation', Noise_Std_Deviation)
    Noise_Signal = np.random.normal(0, Noise_Std_Deviation, SEQ_LENGTH)

    TOA = np.empty(SEQ_LENGTH, dtype='u4')
    # TOA[0] = randint(0,100000) + Noise_Signal[0]
    TOA[0] = 0
    for i in range(1, SEQ_LENGTH):
        TOA[i] = TOA[i - 1] + pri  #+ Noise_Signal[i]

    # value to be entered in the range of 0 to 20
    percentage_of_missing_pulses = random.uniform(0.0, 0.15)  # 5
    print('Missing Pulses', percentage_of_missing_pulses)
    Count_of_dropped_pulses = int(percentage_of_missing_pulses * SEQ_LENGTH)

    index = np.random.randint(0, SEQ_LENGTH, Count_of_dropped_pulses)
    index = np.sort(index)[::-1]
    print(len(index))
    for i in index:
        TOA = np.delete(TOA, i)
  #  print('@@@TOA Len',len(TOA))
    DTOA = Generate_DTOA(TOA=TOA)
    return DTOA
########################################################################################################################
SEQ_LENGTH = 5000
def Generate_Stagger_PRI(pri_value, stagger_level):
    # Value to be entered in the range of 0 to 1 i.e 0, 0.1, 0.2, 0.3 etc
    min_pri = pri_value
    max_pri = pri_value * 1.4
    if (min_pri > 1000):
        max_pri = pri_value + 1000
    input_pri = []
    input_pri.append(pri_value)
    for i in range(stagger_level - 1):
        input_pri.append(round(random.uniform(min_pri, max_pri), 3))
    input_pri.sort(reverse=False)
    #input_pri = [6991, 7098.943, 7117.701, 7389.569, 7570.652, 7619.157]
    print('Pri are(us)', input_pri)
    Noise_Std_Deviation = random.uniform(0.0, 0.9)
    print('Standard Deviation', Noise_Std_Deviation)
    Noise_Signal = np.random.normal(0, Noise_Std_Deviation, SEQ_LENGTH)
    print(max(Noise_Signal))
    TOA = np.empty(SEQ_LENGTH, dtype='u4')
    TOA[0] = randint(0, 100000) #+ Noise_Signal[0]
    i = 0
    while (i < SEQ_LENGTH - 2):
        for j in range(0, len(input_pri)):
            TOA[i + j] = TOA[i + j - 1] + input_pri[j]  + Noise_Signal[i + j]
            if ((i + j) > (SEQ_LENGTH - 2)):
                break
        i = i + len(input_pri)
        # value to be entered in the range of 0 to 20
    percentage_of_missing_pulses =  random.uniform(0.0,0.15) #5
    print(f'Missing Pulses {percentage_of_missing_pulses*100}%')
    Count_of_dropped_pulses = int(percentage_of_missing_pulses * SEQ_LENGTH)
    index = np.random.randint(0, SEQ_LENGTH, Count_of_dropped_pulses)
    index = np.sort(index)[::-1]
    print(len(index))
    for i in index:
        TOA = np.delete(TOA, i)
   # print('@@@TOA Len',len(TOA))
    DTOA = Generate_DTOA(TOA=TOA)
    return DTOA
#######################################################################################################################
def Build_jittered_PRI_DataSet(pri_value):
    # value to to be entered in the range of 100 to 30000
    min_pri = pri_value * 0.90
    max_pri = pri_value * 1.1
    #print('Jittered PRI')
    input_pri = np.random.uniform(min_pri, max_pri, 600)
    print('Min PRI ',input_pri.min())
    print('Max PRI ', input_pri.max())
    # value to be entered in the range of 0 to 20
    percentage_of_missing_pulses = randint(0, 0.0)  # 5
    # Value to be entered in the range of 0 to 1 i.e 0, 0.1, 0.2, 0.3 etc
    Noise_Std_Deviation = round(random.uniform(0.0, 0.9), 3)  # 1
    sequence_length = 3000
    Noise_Signal = np.random.normal(0, Noise_Std_Deviation, sequence_length)
    TOA = np.empty(sequence_length)
    i = 1
    TOA = np.empty(SEQ_LENGTH, dtype='u4')
    TOA[0] = randint(0, 100000) #+ Noise_Signal[0]
    while (i < sequence_length - 2):
        for j in range(0, len(input_pri)):
            TOA[i + j] = TOA[i + j - 1] + input_pri[j] + Noise_Signal[i + j]
            TOA[i + j] = np.round(TOA[i + j], 2)
            if ((i + j) > (sequence_length - 2)):
                break
            # print([i+j])
        i = i + len(input_pri)
  #  print('Jittered PRI')
    Count_of_dropped_pulses = int(percentage_of_missing_pulses * sequence_length )
    drop_list_index = np.random.randint(0, sequence_length - 10, Count_of_dropped_pulses)
    #  .sort(True)
    drop_list_index = np.sort(drop_list_index)[::-1]
    for i in drop_list_index:
        TOA = np.delete(TOA, i)

   # print('Jittered PRI End')
    #print(DTOA_Raw)
    DTOA = Generate_DTOA(TOA=TOA)
    return DTOA

########################################################################################################################
def Generate_TOA(Pri_Category):
    if(Pri_Category == 'CONSTANT'):
        pri = randint(100,10000)  #pri 100us to 5000us
        print('Pri is',pri)
        TOA = Generate_Constant_PRI(pri)
       # print('######## TOA ######\n',TOA)
    elif(Pri_Category == 'STAGGER'):
        pri = randint(100,10000)  #pri 100us to 5000us
        #print('Pri is',pri/10)
        TOA = Generate_Stagger_PRI(pri,randint(2,8))
    elif(Pri_Category == 'JITTER'):
        pri = randint(100,10000)  #pri 100us to 5000us
        print('Pri is',pri)
        TOA = Build_jittered_PRI_DataSet(pri)
        #print('Pri is',pri/10)
    return TOA
########################################################################################################################
def send_pdws(msg):
    # Define the port on which you want to connect
    s = socket.socket()
    time.sleep(1)
    port = 6666
    print('#### Sending PDW ####')
    # connect to the server on local computer
    s.connect(('localhost', port))
    s.send(b'StartPulseAnalysis')
    for i in tqdm(range(0, 30)):
        index = i * 4 * 2 * 50
        bytes_to_send = b'\xf0' + msg[index: index + 4 * 2 * 50]
        # print(bytes_to_send)
        # i = i + 1
        Start_Index = bytes_to_send[1:5]
        Start_Index = int.from_bytes(Start_Index, byteorder='big', signed=False)
        # print('Start Index',Start_Index)
        s.send(bytes_to_send)
        # print("Printed immediately.")
        time.sleep(0.1)
    time.sleep(1)
    s.close()
########################################################################################################################
# print(str(self.combo_Box.currentIndex()))
class Window(QtWidgets.QMainWindow):
    def __init__(self, windowTitle):
        super().__init__()
        self.left = 5
        self.top = 0
        self.width = 800
        self.height = 600
        self.setWindowTitle(windowTitle)
        self.setGeometry(200,  50, 455, 355)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.CustomizeWindowHint)
        self.UiComponents()
        self.show()
    def UiComponents(self):
        self.combo_Box = QtWidgets.QComboBox(self)
        self.combo_Box.setGeometry(QtCore.QRect(150,100,110,30))
        self.combo_Box.setPlaceholderText("Select Signal Type")
        self.combo_Box.addItem("Stable")
        self.combo_Box.addItem("Stagger")
        self.combo_Box.addItem("Jitter")

        self.push_button = QtWidgets.QPushButton("Start",self)
        self.push_button.setGeometry(QtCore.QRect(150,150,100,30))
        self.combo_Box.setCurrentIndex(0)
        self.push_button.clicked.connect(self.SendPdw)
########################################################################################################################
    def SendPdw(self):
        time.sleep(0.1)
        SignalType = self.combo_Box.currentIndex()
        time.sleep(0.1)
        signal = 'CONSTANT'
        if SignalType == 0 :
            print('Stable PRI')
            signal = 'CONSTANT'
        elif SignalType == 1 :
            print('Stegger PRI')
            signal = 'STAGGER'
        elif SignalType == 2 :
            print('Jitter PRI')
            signal = 'JITTER'
        PDW2 = Generate_TOA(signal)
      #  print('############PDW2\n',PDW2)
        PDW1 = np.linspace(start=1,stop=len(PDW2),num = len(PDW2),endpoint=True,dtype ='u4')
       # print('#####PDW1\n',PDW1)
        PDW = np.array(np.column_stack([PDW1, PDW2]).tolist(), dtype = '>u4')
        #y = np.array(x,  dtype='>u4')    #'>u4' is big Endian
        #x = np.array([[3, 1], [2, 3]], dtype='>u4')
        msg = PDW.tobytes()
        send_pdws(msg)
########################################################################################################################
def Main():
    App = QtWidgets.QApplication(sys.argv)
    windowTitle = "PDW Stimulator"
    window = Window(windowTitle)
    sys.exit(App.exec())

if __name__ == "__main__":
    Main()
#######################################################################################################################
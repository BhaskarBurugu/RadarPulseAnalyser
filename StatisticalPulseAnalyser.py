import numpy as np
###########################################################################################################
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
      #  print('Group',count,'LowerPW =',Min_PW + ele[0]*Bin_Width,'END PW=',Min_PW + (ele[1]+1)*Bin_Width)
        PW_List.append((Min_PW + ele[0]*Bin_Width + Min_PW + (ele[1]+1)*Bin_Width)/2)
    #print(PW_List)
    PW_List = [x/1000 for x in PW_List]
    return PW_List
#########################################################################################################
def GetPRI(PRI):
    PRI = [x / 10 for x in PRI if (x < min(PRI) * 2) and x > 100]  # convert to usec and eliminate hormonics
    # print(PW)
    Min_PRI = 100  # MIN PRI 100 us
    Max_PRI = 10000  # Max PRI 10msec = 10,000
    if int(min(PRI) * 0.01) >= 5:
        Bin_Width = 5
    elif int(min(PRI) * 0.01) <= 0:
        Bin_Width = 1
    else:
        Bin_Width = int(min(PRI) * 0.01)
    # Bin_Width = 5 if int(min(PRI) * 0.01) >=5 else int(min(PRI) * 0.01)# 2us
    print('###BIN Width', Bin_Width)
    Number_of_bins = (Max_PRI - Min_PRI) / Bin_Width
    freq, edges = np.histogram(PRI, bins=int(Number_of_bins), range=(Min_PRI, Max_PRI))
    # mode_index = np.argmax(freq)
    # mode_peak = np.max(freq)
    # mode =
    # print (freq)
    # print(edges)
    index = [i for i in range(len(freq)) if freq[i] >= np.max(freq) * 0.3]
    #  print(index)
    group_list = list(group(index))
    print(group_list)
    PRI_List = []
    for count, ele in enumerate(group_list):
        print('Group', count, 'LowerPRI =', Min_PRI + ele[0] * Bin_Width, 'END PRI=',
              Min_PRI + (ele[1] + 1) * Bin_Width)
        PRI_List.append((Min_PRI + ele[0] * Bin_Width + Min_PRI + (ele[1] + 1) * Bin_Width) / 2)
    # print(PW_List)
    nparray_PRI = np.array(PRI)
    print('Std Deviation', np.std(PRI))
    if len(PRI_List) == 1:
        if np.std(PRI) < 2.5:
            PRI_Cat = 'STABLE'
        else:
            PRI_Cat = 'JITTER'
    else:
        PRI_Cat = 'STAGGER LEVEL ' + f'{len(PRI_List)}'

    PRI_Dict = {
        'PRI_Cat': PRI_Cat,
        'PRI': PRI_List,
        'Std Dev': np.std(PRI),
        'Min PRI': np.min(PRI),
        'Max PRI': np.max(PRI)
    }
    return PRI_Dict
###############################################################################################################
PRI1 = 8020 *10
PRI = [(PRI1  + np.random.uniform(-PRI1*0.003,PRI1*0.003)) for _ in range(500)]

PRI_Dict = GetPRI(PRI)
print(min(PRI)/10)
print(max(PRI)/10)
print(PRI_Dict)
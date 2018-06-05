import matplotlib.pyplot as plt
import pandas as pd
import os.path
import zipfile

InputFolder = '../Input'

def load_data(top_file, csv_file, interval = 0.1):
    '''
    Takes in two files, one of which would be original data and second
    is the data after being transforemd into a pandas dataframe.
    This is mostly to ensure I can continue over github as the data files
    can get quite large
    '''
    if os.path.isfile(top_file):
        return read_top_file(top_file, time_interval = interval)
    elif os.path.isfile(csv_file):
        return pd.read_csv(csv_file, header = [0, 1])
    else:
        raise KeyError('Files do not exist')

def save_as_csv(filename, dataframe):
    if not os.path.isfile(filename):
        dataframe.to_csv(filename)
        
    else:
        print('File already exists')
        pass

def stackplot(df, labels, span = [100, 400],
               colors = ["#7bb274", "#a8a495", "#feb308", "#3778bf", "#825f87", '#d9544d', '#ffff7e', '#3b5b92']):
    
    dropped = df.drop(labels, axis = 1)
    to_plot = pd.DataFrame(data = dropped.sum(axis = 1), columns = ['Summed'])
    for x in labels:
        to_plot[x] = df[x]
    
    to_plot[360:400].plot(kind = 'area', figsize = (20, 14))

def setup():
    '''
    This function is used to ensure that every
    zipfile in the inputs folder is extracted
    and dealt with correctly.
    '''

    files = os.listdir(InputFolder)

    files = [InputFolder + '/' + s for s in files]

    for file in files:
        if '.zip' in file:
            if file[:-4] not in files:
                with zipfile.ZipFile(file, 'r') as z:
                    z.extractall(InputFolder)

    for file in files:
        if '.zip' not in file:
            print(file)

def return_files(folder):
    try:
        files = os.listdir(folder)
        files = [folder + '/' + s for s in files]
        return files
    except:
        raise KeyError('Folder does not exist')
        

def parse(input_file, avoid = ["top", "Tasks", "%Cpu(s)", "KiB Mem", "KiB Swap"]):
    
    PIDCPU = {}
    PIDMEM = {}
    
    pid_key = {}
    
    # if not os.path.isfile(newfile):
    with open(input_file) as f:
        for line in f:
            if not any(line.startswith(no) for no in avoid): # This removes the info at start of top
                if not line.isspace(): # Removes empty lines
                    new_line = line.lstrip(' ') # Some lines start with empty spaces
                    sections = new_line.split()
                    PID, CPU, MEM, name = sections[0], sections[8], sections[9], sections[11]
                    if PID == 'PID':
                        pass
                    
                    elif PID not in PIDCPU or PID not in PIDMEM:
                        PIDCPU[PID] = list()
                        PIDCPU[PID].append(float(CPU))
                        
                        PIDMEM[PID] = list()
                        PIDMEM[PID].append(float(MEM))
                        pid_key[PID] = name
                        
                    else:
                        PIDCPU[PID].append(float(CPU))
                        PIDMEM[PID].append(float(MEM))
    
    return PIDCPU, PIDMEM, pid_key

def create_dataframe(cpu_dict, mem_dict, key, time_interval = 0.5):
    '''
    cpu_dict: a Dictionary of lists
    mem_dict: a Dictionary of lists
    
    key = the above two dicts are using PID values as keys.
    Not intuitive for understanding what they mean.
    
    Returns two dataframes, one for cpu and one for mem
    '''
    
    # Turn dicts into Dataframes
    cpu_frame = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in cpu_dict.items() ]))
    mem_frame = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in mem_dict.items() ]))
    
    # Here I am removing every column that has a mean of 0
    cpu_frame = cpu_frame.drop(cpu_frame.columns[cpu_frame.apply(lambda col: col.mean() == 0)], axis=1)
    mem_frame = mem_frame.drop(mem_frame.columns[mem_frame.apply(lambda col: col.mean() == 0)], axis=1)

    # Here I remove every instance of N/A with a 0
    cpu_frame = cpu_frame.fillna(0)
    mem_frame = mem_frame.fillna(0)
    
    # I rename the columns by the their command name. Before they were PID
    cpu_frame.rename(columns = key, inplace = True)
    mem_frame.rename(columns = key, inplace = True)
    
    # I remove duplicate columns here
    cpu_frame = cpu_frame.groupby(cpu_frame.columns, axis=1).sum()
    mem_frame = mem_frame.groupby(mem_frame.columns, axis=1).sum()
    
    # Adding a time index
    df_len = len(cpu_frame)
    cpu_frame['time'] = pd.Series([x * time_interval for x in range(df_len)])
    cpu_frame.set_index('time')
    
    df_len2 = len(mem_frame)
    mem_frame['time'] = pd.Series([x * time_interval for x in range(df_len2)])
    mem_frame.set_index('time')
    
    return cpu_frame, mem_frame

def read_top_file(file, time_interval = 0.1):
    '''
    read_op_file takes in two arguments.
    
    file: Is a string with the location of the top file
    time_interval: The interval between each top measurement
    
    returns a Dataframe containing all the information
    '''
    
    
    # The words I'm avoiding are words that you will find
    # start off the header of all top files
    words_to_avoid = ["top", "Tasks", "%Cpu(s)", "KiB Mem", "KiB Swap"]
    
    # Dataframes can be created from dictionaries
    # So to begin with, I will build up a dictionary that will contain
    # {'process_name' : '[value_at_t0, value_at_t1, value_at_t2, ..., etc.]'}
    proc_dict = {}

    with open(file) as f:
        for line in f:
            if not any(line.startswith(word) for word in words_to_avoid):
                if not line.isspace():
                    
                    # Some lines start with an empty space
                    # e.g: ' 75' 
                    new_line = line.lstrip(' ')
                    sections = new_line.split()
                    
                    PID, CPU, MEM, name = sections[0], sections[8], sections[9], sections[11]
                    
                    if PID == 'PID':
                        pass
                    
                    elif (name, 'CPU') not in proc_dict or (name, 'MEM') not in proc_dict:
                        # Pandas expects dictionaries with multiindex to
                        # contain a tuple as the key.
                        proc_dict[(name, 'CPU')] = list()
                        proc_dict[(name, 'CPU')].append(float(CPU))
                        
                        proc_dict[(name, 'MEM')] = list()
                        proc_dict[(name, 'MEM')].append(float(MEM))
                    
                    else:
                        proc_dict[(name, 'CPU')].append(float(CPU))
                        proc_dict[(name, 'MEM')].append(float(MEM))
    
    # 
    frame = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in proc_dict.items() ]))
    frame = frame.fillna(0)
    
    frame_len = len(frame)
    frame['time'] = pd.Series([x * time_interval for x in range(frame_len)])
    
    return frame

def parseTop(oldfile, newfile, wordsToDelete):
    """
    This function takes in a top file run in batch mode and removes the headers
    The remaining file should only be process information
    """
    if not os.path.isfile(newfile):
        with open(oldfile) as f, open(newfile, "w") as nf:
            for line in f:
                if not any(line.startswith(no) for no in wordsToDelete):    # removes any line that starts with a word in wordsToDelete
                    if not line.isspace():                                  # removes any empty lines
                        nf.write(line.lstrip(' '))                          # The lstrip method is to remove the starting empty space
    else:
        pass

def readFile(file = "result.txt"):
    """
    This function takes in a file and returns lists of all processes as dictionaries
    The dictionaries have the structure of d = {'123': [1, 2, 3, 4, 5]}
    The key is Process ID number and always greater than 0 stored as string
    List contains floats
    """
    
    # PIDCPU will hold a key to a PID
    # number and output a list of CPU used
    # PIDMEM will do the very same
    # thing however with the MEM used

    PIDCPU = {}
    PIDMEM = {}
    if os.path.isfile(file):
        with open(file) as f:
            for line in f:
                if not line.startswith("PID"):
                    s = line.split()

                    # s[0] is the very first string in
                    # the line. This is always PID number

                    if s[0] not in PIDCPU or s[0] not in PIDMEM:
                        # s[8] is the %CPU number
                        PIDCPU[s[0]] = list()
                        PIDCPU[s[0]].append(float(s[8]))

                        # s[9] is the %MEM number
                        PIDMEM[s[0]] = list()
                        PIDMEM[s[0]].append(float(s[9]))
                    else:
                        PIDCPU[s[0]].append(float(s[8]))
                        PIDMEM[s[0]].append(float(s[9]))

            return PIDCPU, PIDMEM
    else:
        print("File does not exist")
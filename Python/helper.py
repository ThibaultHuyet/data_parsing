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

def split_frame(df):
    
    cpu = df.loc[:, (slice(None), 'CPU')]
    mem = df.loc[:, (slice(None), 'MEM')]
    
    cpu.columns = cpu.columns.droplevel(1)
    mem.columns = mem.columns.droplevel(1)
    
    cpu.index.name = 'time'
    mem.index.name = 'time'
    
    return cpu, mem
    
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
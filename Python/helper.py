import pandas as pd
import os.path
import zipfile

InputFolder = '../Input'

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
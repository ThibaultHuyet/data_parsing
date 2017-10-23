import os.path # Used for isfile()
from matplotlib import pyplot as plt
import numpy as np
import matplotlib

def parseTop(oldfile, newfile, wordsToDelete):
	"""
	This function takes in a top file run in batch mode and removes the headers
	The remaining file should only be process information
	"""
	if not os.path.isfile(newfile):
		with open(oldfile) as f, open(newfile, "w") as nf:
			for line in f:
				if not any(line.startswith(no) for no in wordsToDelete):	# removes any line that starts with a word in wordsToDelete
					if not line.isspace():									# removes any empty lines
						nf.write(line.lstrip(' '))							# The lstrip method is to remove the starting empty space
	
	else:
		print("File already exists, are you sure you want to do this?")
		
def returnOne(oldfile, newfile, processName):
    """
    Takes in an oldfile location and a new file location
    old file location is a top batch file
    new file is the oldfile where only one process
    """
    if not os.path.isfile(newfile):
        with open(oldfile) as f, open(newfile, "w") as nf:
            for line in f:
                if processName in line:
                    nf.write(line)

    else:
        print("File already exists")

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
						PIDMEM[s[0]].append(float(s[8]))

			return PIDCPU, PIDMEM
	else:
		print("File does not exist")
	

if __name__ == "__main__":
	FILE = "Text/cpu.txt"
	NEWFILE = "Text/result.txt"

	PI = "Text/pi.txt"
	PIRESULT = "piResult.txt"

	PIPROGRAM = "Text/piProgram.txt"
	PIPROGRESULT = "piProgResult.txt"


	# These are the words that start at the top of the header of "top"
	avoid = ["top", "Tasks", "%Cpu(s)", "KiB Mem", "KiB Swap"]
	# parseTop(FILE, NEWFILE, avoid)
	returnOne(PIPROGRAM, PIPROGRESULT, "main")
	cpu, mem = readFile(PIPROGRESULT)

	print(len(cpu["21540"]))
	# cpu and meme are both dictionaries of lists
	# structure is d = {'key': [1, 2, 3, 4, 5]}
	# key is process ID and values are values over time
	# To graph, I need just the list

	x = np.arange(0, len(cpu['21540']))
	y = cpu['21540']

	plt.plot(x, y)
	plt.xlabel("Time")
	plt.ylabel("cpu")
	plt.show()
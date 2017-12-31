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
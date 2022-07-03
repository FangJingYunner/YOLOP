import os
import json
import scipy.io as spio
import pandas as pd
 
def loadmat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    '''
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)
 
def _check_keys(dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
            dict[key] = _todict(dict[key])
    return dict
 
def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict
 
def mat2json(mat_path=None, filepath = None):
    """
    Converts .mat file to .json and writes new file
    """
 
    matlabFile = loadmat(mat_path)
    #pop all those dumb fields that don't let you jsonize file
    matlabFile.pop('__header__')
    matlabFile.pop('__version__')
    matlabFile.pop('__globals__')
    #jsonize the file - orientation is 'index'
    matlabFile = pd.Series(matlabFile).to_json()
 
    if filepath:
        json_path = os.path.splitext(os.path.split(mat_path)[1])[0] + '.json'
        print(json_path)
        with open(json_path, 'w') as f:
            f.write(matlabFile)
    return matlabFile

if __name__ == '__main__':
    filePath = './'      # revise to the path of .mat files if needed
    for root,dirs,files in os.walk(filePath):
        for f in files:
            if(os.path.splitext(f)[1] == '.mat'):
                mat2json(f, True)
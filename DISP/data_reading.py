import pathlib
import gzip
from decimal import Decimal
import numpy as np

def opener(path):

    """opens a .gz file or an usual file"""

    string = str(path)

    if string[-3:] == ".gz":
        data = gzip.open(string, "rt")
    else:
        data = open(string, "rt")

    return(data)

def gbuilder_parsing(path, model_name):

    data = {}
    free = {}

    gbuilder = opener(path)
    lines = gbuilder.readlines()

    for line in lines:

        line = line.split()

        if len(line)>1:

            if "free" in line and line[0] != '#': #check for which parameters are free or not
                #I am assuming only ONE parameter will be free at a time
                #because I'm not sure how the ordering of the files goes if not
                #Once I know, I'll update this
                #And I assume the mapping is uniform...
                try:
                    if float(line[6]) != 0:
                        free[line[3]] = {"min":float(line[4]),"max":float(line[5]),"res":int(line[6])} #min, max, res
                        key = line[3]
                except:
                    continue

            if line[0] == "static":
                
                x = free.get(line[3])
                if x is not None:
                    step = free[line[3]]["min"]
                    data[line[3]] = [round(step*(i+1),5) for i in range(free[line[3]]["res"])]
                    names = [f"{model_name}-{line[3]}_{num}" for num in data[line[3]]]
                else:
                    try: 
                        data[line[3]] = [float(line[4])]*free[key]["res"] #yes it's overkill to stock it all
                        #but better safe than sorry :)
                    except:
                        data[line[3]] = [line[4]]*free[key]["res"]

    return(data, names)

def sdb_config_parsing(path):

    sdb_config = opener(path)
    lines = sdb_config.readlines()
    model_gp = False

    for line in lines:
        line = line.split()
        if len(line)>0:
            if line[0] == "GAD_SET":
                model_gp = bool(line[1])

    if model_gp == True:
        model_gp = "4G+"
    else:
        model_gp = "4G"

    return(model_gp)

def datatable_mainframe(path):

    if path.is_dir():

        model_name = path.name

        spe_path = ["","",""]

        gbuilder_path, sdb_config_path = '',''

        file_glob = sorted(path.iterdir()) #list of files in input_path directory
        names = [file.name for file in file_glob] # '' if its a dir

        for i,name in enumerate(names): #initial parsing

            if file_glob[i].is_dir():
                folder = [name.split("-"),name.split("_")]
                for folder_name in folder:
                    if "STELUM" in folder_name:
                        spe_path[0] = file_glob[i]
                    elif "PULSE" in folder_name:
                        spe_path[1] = file_glob[i]
                    elif "EIG" in folder_name:
                        spe_path[2] = file_glob[i]

            if name == "gbuilder.conf":

                gbuilder_path = file_glob[i] #to parse names
                data, model_names = gbuilder_parsing(gbuilder_path, model_name)

            if name == "SDB_EVO-std.cf":
                sdb_config_path = file_glob[i] #parsing model_type
                model_type = sdb_config_parsing(sdb_config_path)

        model_list = {"STELUM":[],"PULSE":[],"EIG":[]}
        keys = list(model_list.keys())

        for i,path in enumerate(spe_path):
            if path != "":
                model_list[keys[i]] = sorted(path.iterdir())

        spe = np.zeros((len(data[list(data.keys())[0]]),3))

        if len(model_list["STELUM"]) > 0:
            spe[:,0] = 1
        if len(model_list["PULSE"]) > 0:
            spe[:,1] = 1

        eig_names = model_list["EIG"].copy()
        model_list["EIG"] = [""]*len(model_names)
        for eig in eig_names:
            named = eig.name
            named = named.split("-")
            number = int(named[1])
            model_list["EIG"][number-1] = eig #to account for python indexing
            spe[number,2] = 1

        return(data, model_names, model_list, spe, model_type)
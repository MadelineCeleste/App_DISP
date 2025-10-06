import pathlib
import gzip
from decimal import Decimal
import numpy as np
import pandas as pd

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


def stelum_parsing(path_stelum):

    """Extracts data from format 5m stelum files in a dictionnary of keys:

    dict_keys = ['n','r','mr','rho','p','t','chir','chit','grad','grad_ad','Y','b','lq','mode','fl','fx',
                'lum','eta','etar','kappa','kappar','kappat','grad_rad','zeta','eps','epsr','epst',
                'log10_tau','w','wtau','delr','delp','delt','deltau','dellum','dp','dt','dadmd',
                'ui','duidp','duidt','cp','cv','eta_e','zmoy','gamma',
                'H','He','C','O','rhog']

    Additional information can be found with help(line_number)
    For example help(line_zero) gives the zero line quantity details (n to fx)."""
    data = opener(path_stelum)
    lines = data.readlines()[2:]
    nb_layers = int(lines[-5].split()[0])#need a int for future iterations

    stelum_data = np.zeros(nb_layers*51).reshape(nb_layers,51)
    rows = [lines[i::5] for i in range(0,5)]#this is actually very memory efficient for the loop later
    indexes = [0,16,27,38,46,51]

    #painful way to get floats for our values
    #note that this is much faster than iterating line by line (~2-3 times faster !!).
    #I prefer using numpy arrays for future computations aswell :)
    #Haven't found a faster way to do it *yet*, but it's bloody fast already
    #Most of the bottleneck is not on interpreters, but graphs anyways
    for i in range(nb_layers):
        for j in range(len(rows)):
            try:
                stelum_data[i,indexes[j]:indexes[j+1]] = np.array(list(map(float, rows[j][i].split())))
            except:
                stelum_data[i,indexes[j]:indexes[j+1]] = np.array(list(map(float, rows[j][i].split())))[[0,1,2,3,-1]]
                #So... new data appeared in stelum files recently, no clue why, I have to do something about it, that's the "[0,1,2,3,-1]" for now
                #try..except structure is not ideal, but at least no need to care about those new data for now, whatever they are

    #init of dictionnary keys
    dict_keys = ['n','r','mr','rho','p','t','chir','chit','grad','grad_ad','Y','b','lq','mode','fl','fx',
                'lum','eta','etar','kappa','kappar','kappat','grad_rad','zeta','eps','epsr','epst',
                'log10_tau','w','wtau','delr','delp','delt','deltau','dellum','dp','dt','dadmd',
                'ui','duidp','duidt','cp','cv','eta_e','zmoy','gamma',
                'H','He','C','O','rhog']

    #below, formatting data into a dictionnary, it's intuitive to use for graphs
    stelum_dict = {dict_keys[i]:stelum_data[:,i] for i in range(stelum_data.shape[1])}

    data.close()
    return(stelum_dict)

def data_extraction_static(lines):

    sub_dict_keys = ["ID","L","K","M","Pad","Pnad","sigma",
                "Ekin","Ckl","Kp","Kg","Kp+Kg"]
    
    #should be corrected to work for any stuff, not only for 2
    try:
        pi0 = float(lines[40].split()[0])#extracting pi0, it's always at the same place for Static models
        lines = lines[45:]#lines of non_data, ew
    except:
        pi0=float(lines[41].split()[0])
        lines = lines[46:]#lines of non_data, ew

    l_min = int(lines[0].split()[1])
    l_max = int(lines[-1].split()[1])#need this max l to organize the dictionnary afterwards
    l_indexes = np.linspace(l_min,l_max,(l_max - l_min)+1,dtype=int)
    #I find it very handy to have a subdict of data, with a main dict of keys the "l" values
    pulse_array = np.array([list(map(float, lines[i].split())) for i in range(len(lines))])
    pulse_array = pulse_array[np.where(pulse_array[:,2]<0)]

    l_sorted = []
    for l in l_indexes:
        indexes = np.where(np.int64(pulse_array[:,1]) == l)[0]
        l_sorted.append(pulse_array[indexes,:])
    #above is just creating a list subdivided in l indices, to create the below dictionary

    pulse_dict = {l_indexes[i]:{sub_dict_keys[j]:l_sorted[i][:,j] for j in range(len(sub_dict_keys))} for i in range(len(l_sorted))}

    #there is probably a one-liner for this but eh, who cares, small enough
    for l in l_indexes:
        k_len = len(pulse_dict[l]["K"])
        fixed_ks = np.arange(k_len) + 1
        pulse_dict[l]["K"] = fixed_ks
        pulse_dict[l]["Pi0"] = pi0

    return(pulse_dict)

def data_extraction_evol(lines):

    sub_dict_keys = ["L","K","Pad","Var","Ekin",
                "Ckl","Kp","Kg","Kp+Kg","Ko"]

    lines = lines[9:]
    l_min = int(lines[0].split()[0])
    l_max = int(lines[-1].split()[0])#need this max l to organize the dictionnary afterwards
    l_indexes = np.linspace(l_min,l_max,(l_max - l_min)+1,dtype=int)
    #I find it very practical to have a dict of subdict of data, with a main dict of keys the "l" values
    pulse_array = np.array([list(map(float, lines[i].split())) for i in range(len(lines))])
    pulse_array = pulse_array[np.where(pulse_array[:,1]<0)]

    l_sorted = []
    for l in l_indexes:
        indexes = np.where(np.int64(pulse_array[:,0]) == l)[0]
        l_sorted.append(pulse_array[indexes,:])
    #above is just creating a list subdivided in l indices, to create the below dictionary

    pulse_dict = {l_indexes[i]:{sub_dict_keys[j]:l_sorted[i][:,j] for j in range(len(sub_dict_keys))} for i in range(len(l_sorted))}

    for l in l_indexes:
        k_len = len(pulse_dict[l]["K"])
        fixed_ks = np.arange(k_len) + 1
        pulse_dict[l]["K"] = fixed_ks

    return(pulse_dict)

def pulse_parsing(pulse_string):
    """Extracts data from pulse files in a dictionnary of keys:

    main_dict_keys = int(l_min) to int(l_max) (generally l=1 to l=4)

    Static:
    sub_dict_keys = ["ID","L","K","M","Pad","Pnad","sigma",
                "Ekin","Ckl","Kp","Kg","Kp+Kg","Pi0","Pspacing",
                "Reduced_Pad, "Reduced_Pspacing"]

    Evol:
    sub_dict_keys = ["L","K","Pad","Var","Ekin",
                "Ckl","Kp","Kg","Kp+Kg","Ko","Pspacing",
                "Reduced_Pad, "Reduced_Pspacing"]
    
    Example: pulse_data[1]["Pad"] for adiabatic periods array
    !! This only keeps g-modes !!"""

    data = opener(pulse_string)
    lines = data.readlines()

    try:
        pulse_dict = data_extraction_static(lines)
    except:
        pulse_dict = data_extraction_evol(lines)
    #I mean, if it's not the correct number of line, do the other, it works everytime, why not
    #In practise I can't verify from where the heck it comes from sadly

    pulse_dict = mode_spacing(pulse_dict)

    for l in pulse_dict.keys():
        pulse_dict[l]["Reduced_Pad"] = np.sqrt(l*(l+1))*pulse_dict[l]["Pad"]
        pulse_dict[l]["Reduced_Pspacing"] = np.sqrt(l*(l+1))*pulse_dict[l]["Pspacing"]

    data.close()

    return(pulse_dict)

def mode_spacing(pulse_dict):

    for l in pulse_dict.keys():
        periods = pulse_dict[l]["Pad"]
        rolled_periods = np.roll(pulse_dict[l]["Pad"],axis=0,shift=-1)
        period_spacings = rolled_periods - periods
        pulse_dict[l]["Pspacing"] = period_spacings
        pulse_dict[l]["Pspacing"] = pulse_dict[l]["Pspacing"][:-1] #careful, this becomes None in JSON serialization
        #obviously we always loose a point, mode spacings being a difference

    return(pulse_dict)

def data_parsing(spe, path_stelum, path_pulse):

    data_dict = {"stelum":{}, "pulse":{}}
    if spe[0] == 1:
        data_dict["stelum"] = stelum_parsing(path_stelum)
    if spe[1] == 1:
        data_dict["pulse"] = pulse_parsing(path_pulse)

    return(data_dict)
import numpy as np

def brunt_vaisala_freq(data_dict):

    grav_const = 6.6743e-8 #cgs units

    mr = np.array(data_dict["mr"])
    r = np.array(data_dict["r"])
    rho = np.array(data_dict["rho"])
    p = np.array(data_dict["p"])
    chit = np.array(data_dict["chit"])
    chirho = np.array(data_dict["chir"])
    grad = np.array(data_dict["grad"])
    grad_ad = np.array(data_dict["grad_ad"])
    b = np.array(data_dict["b"])

    g = grav_const*mr/(r**2)

    bv_freq_squared = (g**2)*(rho/p)*(chit/chirho)*(grad_ad - grad + b)

    return(bv_freq_squared)


def lamb_freq(data_dict,l): #so what do we use there ? only l = 1?
    #maybe all 3 and we add the degree thing to stelum as well ? but then it's only active for lamb freq ...

    chirho = data_dict["chir"]
    p = data_dict["p"]
    rho = data_dict["rho"]
    r = data_dict["r"]

    sound_speed_squared = chirho*p/rho
    l_freq_squared = l*(l+1)*sound_speed_squared/(r**2)

    return(l_freq_squared)
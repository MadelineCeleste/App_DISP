import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from pathlib import Path

matplotlib.rcParams['text.usetex'] = True
pathing = "/".join((Path(__file__).parent.__str__()).split("\\")) + "/disp.mplstyle"
print(pathing)
plt.style.use(pathing)


def plt_graph_saving(data, graph_options, x_key, y_key, active_tab):

    
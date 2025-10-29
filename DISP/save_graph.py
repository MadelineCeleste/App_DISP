import numpy as np
from matplotlib import pyplot as plt
import matplotlib
import pathlib
from DISP.global_vars import data, graph_options, line_options
import platform
import logging
import copy

system_os = platform.system()
path = pathlib.Path(__file__).parent.resolve() / "disp.mplstyle"
plt.style.use(path)
matplotlib.use('agg')
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

def plt_graph_saving(dropdown_x_value, dropdown_y_value, active_tab, dropdown_graph_options, output_path, file_prefix, extension):

    if output_path is not None or output_path != "":

        fig, ax = plt.subplots()
        n_models = len(dropdown_graph_options)

        #have to copy because of log scale
        x_opt = copy.deepcopy(graph_options[f"{dropdown_x_value}_x"])
        y_opt = copy.deepcopy(graph_options[f"{dropdown_y_value}_y"])

        x_opt["ranges"] = np.array(x_opt["ranges"])
        y_opt["ranges"] = np.array(y_opt["ranges"])

        if x_opt["scale"] == "log":
            x_opt["ranges"][x_opt["ranges"] < 0 ] = 0.0
        if y_opt["scale"] == "log":
            y_opt["ranges"][y_opt["ranges"] < 0 ] = 0.0

        linestyle_convert = {"dash":"dashed", "solid":"solid"}
        markerstyle_convert = {"circle":"."}

        def draw_func(data_x, data_y, *, graph_label, graph_color, graph_width, graph_style, marker_enabled, marker_color, marker_size, marker_style, marker_bind, **kwargs):

            if kwargs.get("mode_color"):
                graph_color = kwargs["mode_color"]
                marker_color = kwargs["mode_color"]

            if kwargs.get("mode_displayed") and kwargs.get("n_modes"):
                graph_label = f"l{kwargs["mode_displayed"]}"

            if marker_bind == True:
                marker_color = graph_color

            ax_dict = {"color":graph_color,
                    "linewidth":graph_width/2,#rought convertion, both do not draw the same way
                    #plt draws in dpi but go.Figure() draws in pixel...
                    "linestyle":linestyle_convert[graph_style],
                    "label":graph_label}

            if marker_enabled == True:
                ax_dict["marker"] = markerstyle_convert[marker_style]
                ax_dict["markerfacecolor"] = marker_color
                ax_dict["markersize"] = marker_size/2 #same shit

            ax.plot(data_x, data_y, **ax_dict)

        if active_tab == "stelum":

            for option in dropdown_graph_options:

                name = option["label"]
                common_opt = graph_options[name]["common"]
                self_opt = graph_options[name][active_tab]

                data_x = data[name][active_tab][f"{dropdown_x_value}"]
                data_y = data[name][active_tab][f"{dropdown_y_value}"]

                if x_opt["scale"] == "log":
                    data_x = copy.deepcopy(data_x)
                    data_x[data_x <= 0] = np.nan
                if y_opt["scale"] == "log":
                    data_y = copy.deepcopy(data_y)
                    data_y[data_y <= 0] = np.nan

                draw_func(data_x, data_y, **common_opt, **self_opt)

        fig_name = f"{file_prefix}_{dropdown_x_value}_{dropdown_y_value}.{extension}"
        if system_os == "Windows":
            output_path = pathlib.WindowsPath(f"{output_path}") / fig_name
        else:
            output_path = pathlib.PosixPath(f"{output_path}") / fig_name

        if active_tab == "pulse":

            if n_models == 1:

                name = dropdown_graph_options[0]["label"]
                common_opt = graph_options[name]["common"]
                self_opt = graph_options[name][active_tab]

                mode_opt = graph_options[name]["mode"]
                mode_displayed = list(map(int,mode_opt["mode_displayed"].split(",")))
                mode_color = mode_opt["mode_color"].split(";")

                for i, mode in enumerate(mode_displayed):

                    data_x = data[name][active_tab][mode][f'{dropdown_x_value}']
                    data_y = data[name][active_tab][mode][f'{dropdown_y_value}']

                    if x_opt["scale"] == "log":
                        data_x[data_x <= 0] = np.nan
                    if y_opt["scale"] == "log":
                        data_y[data_y <= 0] = np.nan

                    draw_func(data_x, data_y, **common_opt, **self_opt, **{"mode_displayed":mode_displayed[i], "mode_color":mode_color[i], "n_modes":True})

            elif n_models > 1:
                
                for option in dropdown_graph_options:

                    name = option["label"]
                    common_opt = graph_options[name]["common"]
                    self_opt = graph_options[name][active_tab]

                    mode_opt = graph_options[name]["mode"]
                    mode_displayed = int(mode_opt["mode_displayed"].split(",")[0])

                    data_x = data[name][active_tab][mode_displayed][f"{dropdown_x_value}"]
                    data_y = data[name][active_tab][mode_displayed][f"{dropdown_y_value}"]

                    if x_opt["scale"] == "log":
                        data_x[data_x <= 0] = np.nan
                    if y_opt["scale"] == "log":
                        data_y[data_y <= 0] = np.nan

                    draw_func(data_x, data_y, **common_opt, **self_opt, mode_displayed=mode_displayed)

        ax.set_xlabel(rf"${x_opt["label"]}$")
        if x_opt["reversed_axis"] == True:
            x_opt["ranges"] = x_opt["ranges"][::-1]
        ax.set_xscale(x_opt["scale"])

        ax.set_ylabel(rf"${y_opt["label"]}$")
        if y_opt["reversed_axis"] == True:
            y_opt["ranges"] = y_opt["ranges"][::-1]
        ax.set_yscale(y_opt["scale"])

        ax.set_xlim(x_opt["ranges"])
        ax.set_ylim(y_opt["ranges"])

        def add_line(line_label, opt, *, line_value, line_limits, line_direction, line_width, line_style, line_color):

            ranges = opt["ranges"]
            scale = opt["scale"]

            try:
                line_limits = list(map(float,line_limits.split(",")))
            except:
                pass

            line_args = {"linestyle":linestyle_convert[line_style],
                         "linewidth":line_width/2,
                         "color":line_color,
                         "label":line_label}
            if not line_limits:
                w_min, w_max = 0, 1
            elif scale == "log":
                w_min = (np.log10(line_limits[0]) - np.log10(ranges[0])) / (np.log10(ranges[1]) - np.log10(ranges[0]))
                w_max = (np.log10(line_limits[1]) - np.log10(ranges[0])) / (np.log10(ranges[1]) - np.log10(ranges[0]))
            elif scale == "linear":
                w_min = (line_limits[0] - ranges[0])/(ranges[1]-ranges[0])
                w_max = (line_limits[1] - ranges[0])/(ranges[1]-ranges[0])

            if line_direction == "y":
                ax.axhline(y=line_value, xmin=w_min, xmax=w_max, **line_args)
            elif line_direction == "x":
                ax.axvline(x=line_value, ymin=w_min, ymax=w_max, **line_args)

        for line_label in list(line_options[f"{dropdown_x_value}_x"].keys()):
            add_line(line_label, y_opt, **line_options[f"{dropdown_x_value}_x"][line_label])

        for line_label in list(line_options[f"{dropdown_y_value}_y"].keys()):
            add_line(line_label, x_opt, **line_options[f"{dropdown_y_value}_y"][line_label])

        leg = ax.legend(loc="best", frameon=True)
        leg.get_frame().set_alpha(1)
        leg.get_frame().set_edgecolor('black')
        leg.get_frame().set_linewidth(1.0)
        leg.set_zorder(99)

        plt.savefig(output_path, format=extension, dpi=500)
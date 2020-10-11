import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math as mt
from io import StringIO
import os
import sys


# State definitions for top level conversation
SELECTING_ACTION, ADDING_ATHLETE, ADDING_NAME, SELECTING_FEAT, ADDING_PERFORMANCE, SELECTING_PERFORMANCE, PERFORMANCE, TEST = map(chr, range(8))
# State definitions for second level conversation
SELECTING_LEVEL, SELECTING_GENDER = map(chr, range(8, 10))
# State definitions for descriptions conversation
SELECTING_FEATURE, TYPING = map(chr, range(10, 12))
# Meta states
STOPPING, SHOWING = map(chr, range(13, 15))


# Different constants for this example
(PARENTS, CHILDREN, SELF, GENDER, MALE, FEMALE, AGE, NAME, START_OVER, FEATURES,
 CURRENT_FEATURE, CURRENT_LEVEL) = map(chr, range(15, 27))


SELECTING_FEAT, ADDING_NAME, ADD_FEATURES  = map(chr, range(27, 30))

WEIGHT, MAXLOAD, LEAD_RP, LEAD_OS, BOULDER_RP, BOULDER_OS, ATHLETES  = map(chr, range(30, 37))


POT_SBARRA, SOSPENSIONI, KILOS, POWER, DIMENSION, SECONDS  = "POT_SBARRA", "SOSPENSIONI", "KILOS", "POWER", "DIMENSION", "SECONDS"

CURRENT_DAY, SELECT_DAY, TODAY, WRITE_DAY = "CURRENT_DAY", "SELECT_DAY", "TODAY", "WRITE_DAY"

ATHLETE, CONTINUE, MOVE_TO_PERF, PLOT_PERFORMANCE = "ATHLETE", "CONTINUE", "MOVE_TO_PERF", "PLOT_PERFORMANCE"

COLORI, BAR_PLOT_COLOR, CHOOSE_COLORS, SELECTING_DIMENSION, CARICO = "COLORI", "BAR_PLOT_COLOR", "CHOOSE_COLORS", "SELECTING_DIMENSION", "CARICO"

GRAPH_STYLES = "GRAPH_STYLES"

TYPING_2, INPUT_STYLE, STILE_PUNTI, STILE_LINEE, DIMENSIONE_PUNTI, DIMENSIONE_LINEE, DIMENSIONE_TESTO = "TYPING_2", "INPUT_STYLE", "STILE_PUNTI", "STILE_LINEE", "DIMENSIONE_PUNTI", "DIMENSIONE_LINEE", "DIMENSIONE_TESTO"

class Graphic_Utils:

    def autolabel(ax, rects, lab):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for w,rect in zip(lab, rects):
            height = rect.get_height()
            ax.annotate('Kg: {}'.format(w),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', size=6)

        return ax

    def generate_bar_power(athlete_dict, attrs, extra=None, convert_lab=None, colors=None):

        """
            athlete_dict is something like
            {"Giacomo": {"day": [], "pow": [], "kg": []}}

            attrs is a list fo two elements [x_lab, y_values] to be taken from athlete_dict
            for example ["day", "pow"]

            extra is used to plot something on top of the bars froma thlete_dict

            convert_lab is a dict storing axis title from attrs

        """
        #assert len(athlete_dict.keys()) == 1, print("Error")

        athletes = list(athlete_dict.keys()) #athlete names
        num_ath = len(athletes)
        fig, ax = plt.subplots(dpi = 320, figsize=(10,6))

        space = 0.35 + (float((num_ath-1))/num_ath)*0.5
        width = space/num_ath  # the width of the bars
        step = (-width/2)*(num_ath-1)

        for idx, at_name in enumerate(athletes):

            x_lab = athlete_dict[at_name][attrs[0]] #select the one with more days
            y_val = athlete_dict[at_name][attrs[1]]

            x = np.arange(len(x_lab))  # the label locations

            if colors is not None and idx < len(colors):
                rects = ax.bar(x + step, y_val , width, label=at_name, color=colors[idx])
            else:
                rects = ax.bar(x + step, y_val , width, label=at_name)

            step += width
            #rects2 = ax.bar(x + width/2, giacomo_p, width, label='Giacomo', color='dodgerblue')

            # Add some text for labels, title and custom x-axis tick labels, etc.
            if convert_lab is None:
                ax.set_ylabel(attrs[1])
                ax.set_xlabel(attrs[0])
            else:
                ax.set_ylabel(convert_lab[attrs[1]])
                ax.set_xlabel(convert_lab[attrs[0]])


            ax.set_xticks(x)
            ax.set_xticklabels(x_lab, fontsize=8)
            ax.legend()

            if extra is not None:
                ex_lab = athlete_dict[at_name][extra]               
                ax = Graphic_Utils.autolabel(ax, rects, ex_lab)

        
        fig.tight_layout()

        return fig, ax



    def generate_point_suspension(athlete_dict, attrs, extra=None, convert_lab=None, styles=None):

        """
            athlete_dict is something like
            {"Giacomo": {"day": [], "pow": [], "kg": []}}

            attrs is a list fo two elements [x_lab, y_values] to be taken from athlete_dict
            for example ["day", "pow"]

            extra is used to plot something on top of the bars froma thlete_dict

            convert_lab is a dict storing axis title from attrs

        """

        athletes = list(athlete_dict.keys()) #athlete names
        num_ath = len(athletes)
        fig, ax = plt.subplots(dpi = 320, figsize=(10,6))

        plot_dict = {}
        plot_dict = plot_dict.fromkeys(athletes)
        for key in plot_dict.keys():
            plot_dict[key] = {}
            plot_dict[key] = plot_dict[key].fromkeys(np.unique(athlete_dict[key]["dim"]))

            for dims in np.unique(athlete_dict[key]["dim"]):
                plot_dict[key][dims] = {"time": [], "kg": [], "day": []}

        col_id = 0

        for idx, at_name in enumerate(athletes):

            num_load = len(np.unique(athlete_dict[at_name]["kg"]))
            num_dim = len(np.unique(athlete_dict[at_name]["dim"]))


            x_lab = athlete_dict[at_name][attrs[0]] #select the one with more days
            y_val = athlete_dict[at_name][attrs[1]] #select attribute 1
            z_val = athlete_dict[at_name][attrs[2]] #select attribute 2 
            c_val = athlete_dict[at_name][extra]

            for i in range(len(x_lab)):
                day_ = x_lab[i]* len(y_val[i])
                times_ = y_val[i]
                dims_ = z_val[i]
                kgs_ = c_val[i]


                for id_ in range(len(day_)):
                    if type(times_[id_]) == type(kgs_[id_]) == type(day_[id_]) == list:
                        plot_dict[at_name][dims_[id_]]["time"] += times_[id_]
                        plot_dict[at_name][dims_[id_]]["kg"] += kgs_[id_]
                        plot_dict[at_name][dims_[id_]]["day"] += day_[id_]
                    else:
                        plot_dict[at_name][dims_[id_]]["time"].append(times_[id_])
                        plot_dict[at_name][dims_[id_]]["kg"].append(kgs_[id_])
                        plot_dict[at_name][dims_[id_]]["day"].append(day_[id_])

            
            #if there is the dimension 0 it means that we do not have data for that day (filling everything with 0)
            #but it will save it as a new dimension. We cycle on the days without data and for each other dimension
            #if the "0" day is not present we fill the 0 for kg and time. Then we delete the dim=0 data

            if 0 in plot_dict[at_name].keys():
                #extending each dimension with the empty ones
                for i in range(len(plot_dict[at_name][0]["day"])):
                    day = plot_dict[at_name][0]["day"][i]

                    for key in plot_dict[at_name].keys():
                        if key != 0:
                            if day not in plot_dict[at_name][key]["day"]:
                                plot_dict[at_name][key]["day"].append(day)
                                plot_dict[at_name][key]["time"].append(0)
                                plot_dict[at_name][key]["kg"].append(0)

                #deleting the empty (dim = 0)
                del plot_dict[at_name][0]

            for key in plot_dict[at_name].keys():
                label_ = at_name + " Dimension: {} mm".format(str(key))

                x = np.arange(len(plot_dict[at_name][key]["day"]))
                y = plot_dict[at_name][key]["time"] 
                txt = plot_dict[at_name][key]["kg"]

                """

                if colors is not None and col_id < len(colors):
                    scat = ax.plot(x, y, label=label_, color=colors[idx], markersize=10, marker=None)
                else:
                    scat = ax.plot(x, y, label=label_, markersize=10, marker='o')

                """
                scat = ax.plot(x, y, label=label_)
                scat = Graphic_Utils.style_for_plot(scat, col_id, styles)
                fig.canvas.draw()
                fig.canvas.flush_events()

                for ind, txt_ in enumerate(txt):
                    ax.annotate("Kg: {}".format(txt_), (x[ind] + 0.03, y[ind]+0.06), fontsize=10)
                    #ax.text(x * (1 + 0.02), y , i, fontsize=12)

                ax.set_xticks(x)
                ax.set_xticklabels(plot_dict[at_name][key]["day"], fontsize=8)
                ax.legend()

                col_id += 1


            # Add some text for labels, title and custom x-axis tick labels, etc.
            if convert_lab is None:
                ax.set_ylabel("time")
                ax.set_xlabel("days")
            else:
                ax.set_ylabel(convert_lab["time"])
                ax.set_xlabel(convert_lab["days"])
        
        fig.tight_layout()

        return fig, ax


    def plot_power(data, athletes, date_range):

        if len(date_range) == 1:
            date_range = date_range*2

        if type(athletes) == str:
            athletes = [athletes]

        load_allowed = None
        if CARICO in data.keys():
            load_allowed = data[CARICO]



        plot_dict = {}
        plot_dict = plot_dict.fromkeys(athletes)
        for key in plot_dict:
            plot_dict[key] = {}
            plot_dict[key]["days"] = []
            plot_dict[key]["pow"] = []
            plot_dict[key]["kg"] = []

        for key in plot_dict:
            
            start = datetime.datetime.strptime(date_range[0], '%d/%m/%Y')
            end = datetime.datetime.strptime(date_range[1], '%d/%m/%Y')
            step = datetime.timedelta(days=1)
            while start <= end:
                day = str(start.day) + "/" + str(start.month) + "/" + str(start.year)
                if day in data[ATHLETES][key][PERFORMANCE].keys():

                    max_pow = max(data[ATHLETES][key][PERFORMANCE][day][POT_SBARRA][POWER])
                    ind = data[ATHLETES][key][PERFORMANCE][day][POT_SBARRA][POWER].index(max_pow)
                    kg = data[ATHLETES][key][PERFORMANCE][day][POT_SBARRA][KILOS][ind]

                    if load_allowed is None or kg in load_allowed:
                        plot_dict[key]["days"].append(day)
                        plot_dict[key]["pow"].append(max_pow)
                        plot_dict[key]["kg"].append(kg)

                    elif load_allowed is not None and kg not in load_allowed:
                        plot_dict[key]["days"].append(day)
                        plot_dict[key]["pow"].append(0)
                        plot_dict[key]["kg"].append(0)

                else:
                    plot_dict[key]["days"].append(day)
                    plot_dict[key]["pow"].append(0)
                    plot_dict[key]["kg"].append(0)
                
                start += step

        print(plot_dict)
        
        if COLORI in data.keys():
            fig, ax = Graphic_Utils.generate_bar_power(plot_dict, ["days", "pow"], extra="kg", convert_lab={"days": "days", "pow": "Power (W)"}, colors=data[COLORI])
        else:
            fig, ax = Graphic_Utils.generate_bar_power(plot_dict, ["days", "pow"], extra="kg", convert_lab={"days": "days", "pow": "Power (W)"})

        
        return fig, ax


    def plot_suspensions(data, athletes, date_range):

        if len(date_range) == 1:
            date_range = date_range*2

        if type(athletes) == str:
            athletes = [athletes]

        load_allowed = None
        len_alload = 0
        if CARICO in data.keys():
            load_allowed = data[CARICO]
            len_alload = len(data[CARICO])

        dimension_allowed = None
        len_aldim = 0
        if DIMENSION in data.keys():
            dimension_allowed = data[DIMENSION]
            len_aldim = len(data[DIMENSION])
            

        plot_dict = {}
        plot_dict = plot_dict.fromkeys(athletes)
        for key in plot_dict:
            plot_dict[key] = {}
            plot_dict[key]["days"] = []
            plot_dict[key]["time"] = []
            plot_dict[key]["dim"] = []
            plot_dict[key]["kg"] = []   

        for key in plot_dict:
            start = datetime.datetime.strptime(date_range[0], '%d/%m/%Y')
            end = datetime.datetime.strptime(date_range[1], '%d/%m/%Y')
            step = datetime.timedelta(days=1)
            while start <= end:
                day = str(start.day) + "/" + str(start.month) + "/" + str(start.year)
                if day in data[ATHLETES][key][PERFORMANCE].keys():
                    
                    allowed_time = []  
                    allowed_dim = []
                    allowed_kg = []

                    for i in range(len(data[ATHLETES][key][PERFORMANCE][day][SOSPENSIONI][SECONDS])):
                        kg = data[ATHLETES][key][PERFORMANCE][day][SOSPENSIONI][KILOS][i]
                        sec = data[ATHLETES][key][PERFORMANCE][day][SOSPENSIONI][SECONDS][i]
                        dim = data[ATHLETES][key][PERFORMANCE][day][SOSPENSIONI][DIMENSION][i]

                        if load_allowed is None or kg in load_allowed:
                            if dimension_allowed is None or dim in dimension_allowed:
                                allowed_time.append(sec)
                                allowed_dim.append(dim)
                                allowed_kg.append(kg)


                    if len(allowed_kg) > 0 :
                        plot_dict[key]["days"].append([day]*len(allowed_kg))
                        plot_dict[key]["kg"].append(list(allowed_kg))
                        plot_dict[key]["time"].append(list(allowed_time))
                        plot_dict[key]["dim"].append(list(allowed_dim))

                    else:
                        plot_dict[key]["days"].append([day])
                        plot_dict[key]["kg"].append([0])
                        plot_dict[key]["time"].append([0])
                        plot_dict[key]["dim"].append([0])

                else:
                    plot_dict[key]["days"].append([day])
                    plot_dict[key]["kg"].append([0])
                    plot_dict[key]["time"].append([0])
                    plot_dict[key]["dim"].append([0])
                
                start += step


        """
        if COLORI in data.keys():
            fig, ax = Graphic_Utils.generate_point_suspension(plot_dict, ["days", "time", "dim", "kg"], extra="kg", convert_lab={"days": "Day", "time": "Time (s)", "kg": "Load (Kg)", "dim": "Dimension (mm)"}, colors=data[COLORI])
        else:
            fig, ax = Graphic_Utils.generate_point_suspension(plot_dict, ["days", "time", "dim", "kg"], extra="kg", convert_lab={"days": "Day", "time": "Time (s)", "kg": "Load (Kg)", "dim": "Dimension (mm)"})
        """ 

        styles_ = Graphic_Utils.retrieve_plot_info(data)

        fig, ax = Graphic_Utils.generate_point_suspension(plot_dict, ["days", "time", "dim", "kg"], extra="kg", convert_lab={"days": "Day", "time": "Time (s)", "kg": "Load (Kg)", "dim": "Dimension (mm)"}, styles=styles_)
        
        return fig, ax


    def retrieve_plot_info(data):

        s = {"Colors":[], "Line_style": [], "Line_width": [], "Marker_size": [], "Marker_style": [], "Text_size": []}
    

        if GRAPH_STYLES not in data.keys():
            return s 

        else:
            styles = data[GRAPH_STYLES]

            if COLORI in styles.keys():
                s["Colors"] = styles[COLORI]
            
            if STILE_LINEE in styles.keys():
                s["Line_style"] = styles[STILE_LINEE]

            if DIMENSIONE_LINEE in styles.keys():
                s["Line_width"] = styles[DIMENSIONE_LINEE]

            if DIMENSIONE_PUNTI in styles.keys():
                s["Marker_size"] = styles[DIMENSIONE_PUNTI]

            if STILE_PUNTI in styles.keys():
                s["Marker_style"] = styles[STILE_PUNTI]

            if DIMENSIONE_TESTO in styles.keys():
                s["Text_size"] = styles[DIMENSIONE_TESTO]

            return s

    def style_for_plot(lines, id_, styles):

        #return same if style are empty:
        ret = True
        for key in styles.keys():
            #print(key, styles[key])
            if len(styles[key]) != 0: ret = False

        if ret: return pl

        for key in styles.keys():
            if len(styles[key]) > 0:
                if id_ < len(styles[key]):
                    prop = styles[key][id_]
                else:
                    prop = styles[key][-1]

                for pl in lines:
                    if key == "Colors":
                        pl.set_color(prop)
                    if key == "Line_style":
                        pl.set_linestyle(prop)
                    if key == "Line_width":
                        pl.set_linewidth(prop)
                    if key == "Marker_size":
                        pl.set_markersize(prop)
                    if key == "Marker_style":
                        pl.set_marker(prop)

        return pl

            






        

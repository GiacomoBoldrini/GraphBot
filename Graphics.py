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


    def plot_power(data, athletes, date_range):

        if len(date_range) == 1:
            date_range = date_range*2

        if type(athletes) == str:
            athletes = [athletes]

        load_allowed = None
        if CARICO in data.keys():
            load_allowed = data[CARICO]


        print(load_allowed)


        plot_dict = {}
        plot_dict = plot_dict.fromkeys(athletes)
        for key in plot_dict:
            plot_dict[key] = {}
            plot_dict[key]["days"] = []
            plot_dict[key]["pow"] = []
            plot_dict[key]["kg"] = []

        for key in plot_dict:
            print("Atleta: {}".format(key))
            print(data[ATHLETES][key][PERFORMANCE])
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



        

import pandas as pd
import numpy as np
from final_prediction import predict
from timedistance import analyze_median_timedistance
from merging import *
from results import *
from interaction import *
from preprocessing import preprocessing


if __name__ == '__main__':

    tree_string = ""

    rawdata, set_of_actions = preprocessing("Data.csv", 6, 8114, "sensor", ";")
    save_process_as_png(rawdata, 0)
    save_abstraction_as_csv(rawdata, 0)
    for level_of_abstraction in range(1, 16):
        stop_abstracting = False
        sorted_pair_array, sorted_pair_labels = predict(
            rawdata, set_of_actions, 3, 5, "CaseID", 14)

        for i in range(len(sorted_pair_array)):

            e1 = set_of_actions[sorted_pair_labels[0, i]]
            e2 = set_of_actions[sorted_pair_labels[1, i]]
            answer = ask_user(e1, e2, sorted_pair_array[i])

            if answer == "Yes":

                tree_string = build_abstraction_tree(
                    e1, e2, level_of_abstraction, tree_string)

                rawdata, nr_events_abstracted, set_of_actions = abstract_log(
                    e1, e2, e1 + e2, rawdata)

                print("Abstracted {} Events".format(nr_events_abstracted))
                print(f"Now you only have {len(set_of_actions)} actions")

                rawdata = delete_repetitions(rawdata)
                save_process_as_png(rawdata, level_of_abstraction)
                save_abstraction_as_csv(rawdata, level_of_abstraction)

                generate_tree(tree_string)
                break
            elif answer == "Stop":
                stop_abstracting = True
                break
            elif answer == "No":
                continue
        if stop_abstracting:
            break

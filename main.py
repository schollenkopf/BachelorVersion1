import pandas as pd
import numpy as np
import datetime
import statistics as stat
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
from pm4py.util import constants


def read_data(filename, number_columns, number_rows, event_label_column, separator):
    rawdata = pd.read_csv(filename, separator, usecols=range(number_columns), nrows=number_rows)  # More stuff to parametrize
    set_of_actions = list(rawdata[event_label_column].unique())
    return rawdata, set_of_actions


def analyze_mean_timedistance(rawdata, set_of_actions,timestamp_column,action_column, trace_ID, number_of_traces):
    # watch out for division by 0
    sum_time = np.zeros((len(set_of_actions), len(set_of_actions)))
    n_time = np.zeros((len(set_of_actions), len(set_of_actions)))

    for trace in range(1, number_of_traces + 1):
        timestamps_of_previous_events = {}

        for event in rawdata[rawdata[trace_ID] == trace].values:
            current_action = event[action_column]
            time = event[timestamp_column]
            time = convert_to_seconds(time)

            for action in timestamps_of_previous_events.keys():
                for p_time in timestamps_of_previous_events[action]:
                    sum_time[set_of_actions.index(action), set_of_actions.index(
                        current_action)] += abs(time - p_time)
                    n_time[set_of_actions.index(action), set_of_actions.index(
                        current_action)] += 1
                    sum_time[set_of_actions.index(current_action),
                             set_of_actions.index(action)] += abs(time - p_time)
                    n_time[set_of_actions.index(current_action),
                           set_of_actions.index(action)] += 1

            if current_action in timestamps_of_previous_events.keys():
                previous_occurences = timestamps_of_previous_events[current_action]
                previous_occurences.append(time)
                timestamps_of_previous_events[current_action] = previous_occurences
            else:
                timestamps_of_previous_events[current_action] = [time]

    mean_time = sum_time / n_time
    return mean_time

def analyze_median_timedistance(rawdata, set_of_actions,timestamp_column,action_column, trace_ID, number_of_traces):
    all_times = [[[] for i in range(len(set_of_actions))] for j in range(len(set_of_actions))] 

    for trace in range(1, number_of_traces + 1):
        timestamps_of_previous_events = {}
        for event in rawdata[rawdata[trace_ID] == trace].values:
            current_action = event[action_column]
            time = event[timestamp_column]
            time = convert_to_seconds(time)

            for action in timestamps_of_previous_events.keys():
                for p_time in timestamps_of_previous_events[action]:
                    all_times[set_of_actions.index(action)][set_of_actions.index(
                        current_action)].append(abs(time - p_time))
                    
                    all_times[set_of_actions.index(current_action)][
                             set_of_actions.index(action)].append(abs(time - p_time))

            if current_action in timestamps_of_previous_events.keys():
                previous_occurences = timestamps_of_previous_events[current_action]
                previous_occurences.append(time)
                timestamps_of_previous_events[current_action] = previous_occurences
            else:
                timestamps_of_previous_events[current_action] = [time]

    medians = np.zeros((len(set_of_actions), len(set_of_actions)))
    for a1 in range(len(set_of_actions)):
        for a2 in range(len(set_of_actions)):
            medians[a1, a2] = stat.median(all_times[a1][a2]) if len(all_times[a1][a2]) > 0 else np.inf
    print(medians)
    return medians


def sort_results(mean_time, set_of_actions):
    # sort sensor pairs based on average distance
    l = len(set_of_actions)
    n = 0
    number_of_pairs = int((l*l)/2-l/2)
    pair_labels = np.zeros((2, number_of_pairs), dtype=int)
    pair_array = np.zeros(number_of_pairs)

    for i in range(l):
        for j in range(l):
            if j > i:
                pair_labels[0, n] = i
                pair_labels[1, n] = j
                pair_array[n] = mean_time[i, j]

                n = n + 1
    # print(pair_labels)
    # print(pair_array)

    pair_array_indces = np.argsort(pair_array)
    sorted_pair_array = pair_array[pair_array_indces]
    sorted_pair_labels = pair_labels[:, pair_array_indces]

    return sorted_pair_array, sorted_pair_labels


def delete_repetitions(datalog):
    ids_to_delete = []
    n = 0
    for trace in range(1, int(datalog.values[-1, 0]) + 1):
        last_event = []
        average_time = np.array([])
        for event in datalog[datalog.CaseID == trace].values:
            if len(last_event) > 0 and last_event[5] == event[5]:
                average_time = np.append(
                    average_time, convert_to_seconds(last_event[3]))
                ids_to_delete.append(n)
            if len(average_time) > 0 and last_event[5] != event[5]:
                # Maybe keep track also of the other proprieties, not only time
                datalog.at[n - 1,
                           'timestamp'] = convert_to_datatime(average_time.mean())
                average_time = np.array([])
            last_event = event
            n += 1
    datalog = datalog.drop(labels=ids_to_delete, axis=0)
    datalog = datalog.reset_index(drop=True)
    return datalog


def convert_to_seconds(time):
    return datetime.datetime.strptime(
        time[0:26], "%Y-%m-%dT%H:%M:%S.%f").timestamp()


def convert_to_datatime(time):
    return datetime.datetime.fromtimestamp(time).strftime("%Y-%m-%dT%H:%M:%S.%f")


def abstract_log(set_of_actions1, set_of_actions2, newname, rawdata):
    n = 0
    nr_events_abstracted = 0
    for event in rawdata.values:
        if event[5] == set_of_actions1 or event[5] == set_of_actions2:
            nr_events_abstracted += 1
            rawdata.at[n, 'sensor'] = newname
        n += 1
    set_of_actions = list(rawdata.sensor.unique())
    return rawdata, nr_events_abstracted, set_of_actions


if __name__ == '__main__':

    tree_string = ""

    rawdata, set_of_actions = read_data("Data.csv", 6, 8114, "sensor", ";")
    rawdata = delete_repetitions(rawdata)
    rawdata.to_csv("Abstraction0.csv")
    for level_of_abstraction in range(1, 16):
        out = False
        timedistance = analyze_median_timedistance(rawdata, set_of_actions,3,5,"CaseID",14)
        sorted_pair_array, sorted_pair_labels = sort_results(
            timedistance, set_of_actions)
        print(f"Now you only have {len(set_of_actions)}")

        for i in range(len(sorted_pair_array)):
            
            print("Do you want to abstract:")
            print(set_of_actions[sorted_pair_labels[0, i]] +
                  "-" + set_of_actions[sorted_pair_labels[1, i]])
            print("The time distance between them is:")
            print(sorted_pair_array[i])
            #print(" Type Yes or No or Stop")
            answer = input(" Type Yes or No or Stop")
            if answer == "Yes":
                e1 = set_of_actions[sorted_pair_labels[0, i]]
                e2 = set_of_actions[sorted_pair_labels[1, i]]
                tree_string = tree_string +  e1 + "->" + e1 + e2 + "[label = " + str(level_of_abstraction) + "]" + ";"
                tree_string = tree_string + e2 + "->" + e1 + e2 + "[label = " + str(level_of_abstraction) + "]"+ ";"
                rawdata, nr_events_abstracted, set_of_actions = abstract_log(
                    set_of_actions[sorted_pair_labels[0, i]], set_of_actions[sorted_pair_labels[1, i]], set_of_actions[sorted_pair_labels[0, i]] + set_of_actions[sorted_pair_labels[1, i]], rawdata)
                print("Abstracted {} Events".format(nr_events_abstracted))
                print(rawdata)
                rawdata = delete_repetitions(rawdata)
                rawdata.to_csv("Abstraction" +
                               str(level_of_abstraction) + ".csv")
                log_csv = dataframe_utils.convert_timestamp_columns_in_df(rawdata)
                log_csv.rename(columns={'CaseID': 'case'}, inplace=True)
                parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'case',
                              constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "sensor", 
                              constants.PARAMETER_CONSTANT_TIMESTAMP_KEY: "time:timestamp"}
                event_log = log_converter.apply(log_csv, parameters=parameters, variant=log_converter.Variants.TO_EVENT_LOG)
                heu_net = heuristics_miner.apply_heu(event_log, parameters=parameters)
                gviz = hn_visualizer.apply(heu_net)
                hn_visualizer.view(gviz)
                break
            elif answer == "Stop":
                out = True
                break
            elif answer == "No":
                continue
        if out:
            break
    print(tree_string)  

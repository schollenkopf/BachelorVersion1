from operator import truediv
from this import d
import pandas as pd
import numpy as np
import datetime


def read_data(filename):
    rawdata = pd.read_csv(filename, ";", usecols=[
        0, 1, 2, 3, 4, 5], nrows=8114)  # More stuff to parametrize
    actions = list(rawdata.sensor.unique())
    return rawdata, actions


def analyze_timedistance(rawdata, actions):
    sum_time = np.zeros((len(actions), len(actions)))
    n_time = np.zeros((len(actions), len(actions)))

    for trace in range(1, rawdata.values[-1, 0] + 1):
        time_occurrences = {}
        for event in rawdata[rawdata.CaseID == trace].values:
            current_action = event[5]
            time = event[3]
            time = convert_to_seconds(time)

            for action in time_occurrences.keys():
                for p_time in time_occurrences[action]:
                    sum_time[actions.index(action), actions.index(
                        current_action)] += abs(time - p_time)
                    n_time[actions.index(action), actions.index(
                        current_action)] += 1
                    sum_time[actions.index(current_action),
                             actions.index(action)] += abs(time - p_time)
                    n_time[actions.index(current_action),
                           actions.index(action)] += 1

            if current_action in time_occurrences.keys():
                previous_occurences = time_occurrences[current_action]
                previous_occurences.append(time)
                time_occurrences[current_action] = previous_occurences
            else:
                time_occurrences[current_action] = [time]

    mean_time = sum_time / n_time
    return mean_time


def sort_results(mean_time, actions):
    # sort sensor pairs based on average distance
    l = len(actions)
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


def abstract_log(actions1, actions2, newname, rawdata):
    n = 0
    nr_events_abstracted = 0
    for event in rawdata.values:
        if event[5] == actions1 or event[5] == actions2:
            nr_events_abstracted += 1
            rawdata.at[n, 'sensor'] = newname
        n += 1
    actions = list(rawdata.sensor.unique())
    return rawdata, nr_events_abstracted, actions


if __name__ == '__main__':

    rawdata, actions = read_data("Data.csv")
    rawdata = delete_repetitions(rawdata)
    print(rawdata)
    for level_of_abstraction in range(1, 16):

        out = False
        mean_time = analyze_timedistance(rawdata, actions)
        sorted_pair_array, sorted_pair_labels = sort_results(
            mean_time, actions)
        print(f"Now you only have {len(actions)}")

        for i in range(len(sorted_pair_array)):
            print("Do you want to abstract:")
            print(actions[sorted_pair_labels[0, i]] +
                  "-" + actions[sorted_pair_labels[1, i]])
            print("The time distance between them is:")
            print(sorted_pair_array[i])
            #print(" Type Yes or No or Stop")
            answer = input(" Type Yes or No or Stop")
            if answer == "Yes":
                rawdata, nr_events_abstracted, actions = abstract_log(
                    actions[sorted_pair_labels[0, i]], actions[sorted_pair_labels[1, i]], actions[sorted_pair_labels[0, i]] + "-" + actions[sorted_pair_labels[1, i]], rawdata)
                print("Abstracted {} Events".format(nr_events_abstracted))
                print(rawdata)
                rawdata = delete_repetitions(rawdata)
                rawdata.to_csv("Abstraction" +
                               str(level_of_abstraction) + ".csv")
                break
            elif answer == "Stop":
                out = True
                break
            elif answer == "No":
                continue
        if out:
            break

import numpy as np
from timedistance import *


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


def max(array):
    if np.max(array) == np.inf:
        return np.max(array[array < np.inf])
    return np.max(array)


def predict(rawdata, set_of_actions, timestamp_column, action_column, trace_ID, number_of_traces):
    timedistance = analyze_median_timedistance(
        rawdata, set_of_actions, timestamp_column, action_column, trace_ID, number_of_traces, "median")
    timedistance_std = analyze_median_timedistance(
        rawdata, set_of_actions, timestamp_column, action_column, trace_ID, number_of_traces, "stdev")
    combined = (timedistance / (max(timedistance) - np.min(timedistance))) * (timedistance_std / (max(timedistance_std) - np.min(timedistance_std)))
    sorted_pair_array, sorted_pair_labels = sort_results(
        combined, set_of_actions)
    return sorted_pair_array, sorted_pair_labels

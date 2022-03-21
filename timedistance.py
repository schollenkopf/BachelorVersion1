import numpy as np
from file_handling import convert_to_datatime, convert_to_seconds
import statistics as stat


def analyze_mean_timedistance(rawdata, set_of_actions, timestamp_column, action_column, trace_ID, number_of_traces):
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


def analyze_median_timedistance(rawdata, set_of_actions, timestamp_column, action_column, trace_ID, number_of_traces):
    all_times = [[[] for i in range(len(set_of_actions))]
                 for j in range(len(set_of_actions))]

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
            medians[a1, a2] = stat.median(all_times[a1][a2]) if len(
                all_times[a1][a2]) > 0 else np.inf
    return medians

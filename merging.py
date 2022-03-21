import numpy as np
from file_handling import convert_to_seconds, convert_to_datatime
import pandas as pd


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

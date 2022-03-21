import datetime
import pandas as pd


def read_data(filename, number_columns, number_rows, event_label_column, separator):
    rawdata = pd.read_csv(filename, separator, usecols=range(
        number_columns), nrows=number_rows)  # More stuff to parametrize
    set_of_actions = list(rawdata[event_label_column].unique())
    return rawdata, set_of_actions


def convert_to_seconds(time):
    return datetime.datetime.strptime(
        time[0:26], "%Y-%m-%dT%H:%M:%S.%f").timestamp()


def convert_to_datatime(time):
    return datetime.datetime.fromtimestamp(time).strftime("%Y-%m-%dT%H:%M:%S.%f")

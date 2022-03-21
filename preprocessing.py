from file_handling import read_data
from merging import delete_repetitions


def preprocessing(filename, number_columns, number_rows, event_label_column, separator):
    rawdata, set_of_actions = read_data(
        filename, number_columns, number_rows, event_label_column, separator)
    rawdata = delete_repetitions(rawdata)
    return rawdata, set_of_actions

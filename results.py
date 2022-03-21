from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
from pm4py.util import constants
import graphviz


def save_process_as_png(rawdata, level_of_abstraction):
    parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'CaseID',
                  constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "sensor",
                  constants.PARAMETER_CONSTANT_TIMESTAMP_KEY: "timestamp"}
    event_log = log_converter.apply(
        rawdata, parameters=parameters, variant=log_converter.Variants.TO_EVENT_LOG)
    heu_net = heuristics_miner.apply_heu(event_log, parameters=parameters)
    gviz = hn_visualizer.apply(heu_net)
    hn_visualizer.save(gviz, "abstractions_images/Abstraction" +
                       str(level_of_abstraction) + ".png")


def save_abstraction_as_csv(rawdata, level_of_abstraction):
    rawdata.to_csv("abstractions/Abstraction" +
                   str(level_of_abstraction) + ".csv")


def build_abstraction_tree(e1, e2, level_of_abstraction, tree_string):
    tree_string = tree_string + e1 + "->" + e1 + e2 + \
        "[label = " + str(level_of_abstraction) + "]" + ";"
    tree_string = tree_string + e2 + "->" + e1 + e2 + \
        "[label = " + str(level_of_abstraction) + "]" + ";"
    return tree_string


def generate_tree(tree_string):
    dot = graphviz.Source(
        'digraph "the holy hand grenade" { ' + tree_string + '}')
    dot.format = 'png'
    dot.render(directory='abstraction_tree/')

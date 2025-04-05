import numpy as np
import scipy.stats as stats
import networkx as nx


ARRIVAL_RATE = np.array([314.2, 162.4, 138.6, 148.8, 273.2, 1118.8, 2773.8, 4036.2, 4237.4, 3277.0, 2843.0, 2876.4, 3143.0, 3277.8, 3546.2, 4335.0, 4945.4, 4525.8, 2847.8, 1828.0, 1378.4, 1271.2, 1171.2, 767.6])
INCIDENT_RATE = np.array([0.1935483870967742, 0.25806451612903225, 0.2903225806451613, 0.1935483870967742, 0.06451612903225806, 0.967741935483871, 32.16129032258065, 131.03225806451613, 157.2258064516129, 48.32258064516129, 8.451612903225806, 6.258064516129032, 8.161290322580646, 10.290322580645162, 19.0, 65.7741935483871, 157.41935483870967, 163.3548387096774, 36.54838709677419, 3.7096774193548385, 1.2258064516129032, 0.8709677419354839, 0.5806451612903226, 0.41935483870967744])
INCIDENT_DURATION_PARAMS = (1.2294425495153518, 0.09878316410683122, 5.082687545787541)
incident_duration_dist = stats.lognorm(*INCIDENT_DURATION_PARAMS)
MEAN_ACCIDENT_DURATION = 1

Graph = nx.read_gml('./data/networkAssignment.gml')
Graph = Graph.to_directed()
JUNCTIONS = list(Graph.nodes)

DIC_EDGES = {}

DIC_ACCIDENTS = {}

for edge in Graph.edges:
    DIC_EDGES[edge] = []
    DIC_ACCIDENTS[edge] = 0
    #Associate departure from queue distribution to each edge based on number of lanes
    rate = 0.2/(60 * Graph.edges[edge]['lanes'])
    Graph.edges[edge]['DepDist'] = stats.expon(scale = rate)

    Graph.edges[edge]['accident'] = False
    Graph.edges[edge]['queue'] = False
    # Graph.edges[edge]['accident_duration'] = 0
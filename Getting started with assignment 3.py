import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from shapely.geometry.linestring import LineString



################################
# The assignment graph
################################

assignmentGraph = nx.read_gml('networkAssignment.gml')


# Show the node data
print('Assignment Graph\n----------------\n')
print(f'Number of nodes: {len(assignmentGraph.nodes)}')
for k in assignmentGraph.nodes:
    print(f"{k} respresents {assignmentGraph.nodes[k]['name']}")
    
# Show the edge data
print(f'Number of edges: {len(assignmentGraph.edges)}')
for k in assignmentGraph.edges:
    en = assignmentGraph.edges[k]
    print(f"{assignmentGraph.edges[k]['name']} has {assignmentGraph.edges[k]['lanes']} lanes")
    




# Find a route in the network
allJunctions = list(assignmentGraph.nodes)
fromJunction = allJunctions[1]  # Leenderheide
toJunction = allJunctions[14]     # Ridderkerk
rt = nx.shortest_path(assignmentGraph,fromJunction,toJunction, weight='length')
rtLength = nx.shortest_path_length(assignmentGraph,fromJunction,toJunction, weight='length') / 1000


# Print the route
print(f"Assignment Graph Route from {assignmentGraph.nodes[fromJunction]['name']} to {assignmentGraph.nodes[toJunction]['name']}:")
print(f'Total route length: {rtLength} km')
for i in range(len(rt) - 1):
    j1 = assignmentGraph.nodes[rt[i]]['name']
    j2 = assignmentGraph.nodes[rt[i + 1]]['name']
    
    # An edge in the assignment graph is represented by a tuple of 2 nodes.
    # Remember: this graph is UNdirected!
    
    edg = (rt[i], rt[i + 1])
    length = assignmentGraph.edges[edg]['length'] / 1000  # convert meters to km
    nrLanes = 0
    if 'lanes' in assignmentGraph.edges[edg].keys(): 
        nrLanes = int(assignmentGraph.edges[edg]['lanes'] )
    print(f'{j1} -> {j2} : length = {length} km, nr of lanes = {nrLanes}')
    


    

# Plot the assignment graph and the route

posDict = {}
junctionLabelsDict = {}
for k in assignmentGraph.nodes:
    posDict[k] = (assignmentGraph.nodes[k]['x'], assignmentGraph.nodes[k]['y'])
    junctionLabelsDict[k] = assignmentGraph.nodes[k]['name']

route_coords = np.array([posDict[r] for r in rt])

plt.figure(figsize=(10,10))
nx.draw(assignmentGraph, pos=posDict, labels=junctionLabelsDict, node_size=300, arrows=False)
plt.plot(route_coords[:,0], route_coords[:,1], 'r', linewidth=5)
plt.show()

    



# Some other useful NetworkX functions, applied to the assignment graph


# Find node id of a given name

ids = [n for n in assignmentGraph.nodes if assignmentGraph.nodes[n]['name'] == 'Knooppunt Batadorp']
print(ids[0])

# get all the ids plus names in a dictionary:
print(assignmentGraph.nodes.data('name'))

# same for the edge lengths
print(assignmentGraph.edges.data('length'))


# create a copy of a graph and add a property 'travel time' to each edge
maxSpeed = 100  # km/h

assignmentGraph2 = nx.Graph(assignmentGraph)
for e in assignmentGraph2.edges:
    assignmentGraph2.edges[e]['traveltime'] = assignmentGraph2.edges[e]['length'] / 1000 / maxSpeed


rt = nx.shortest_path(assignmentGraph2,fromJunction,toJunction, weight='traveltime')
rtTime = nx.shortest_path_length(assignmentGraph2,fromJunction,toJunction, weight='traveltime') * 60 # route travel time in minutes
print(f'Time to travel route is: {rtTime}  minutes')




##########################################################################################################
#
# Everything below this line is OPTIONAL! You do not have to use these networks,
# but you might find this more challenging.
# - networkNLjunctions.gml really has the exact same structure as networkAssignment.gml,
#   but it contains ALL junctions and links in the Netherlands, not just the selected area.
# - networkNLcomplete.gml also contains the map of the Netherlands, but has MANY more junctions
#   and links. It does contain the actual graphical layout of all the roads, as you can see in the plot.
#
##########################################################################################################




##########################################################
# The graph with all major junctions in The Netherlands
##########################################################

junctionGraph = nx.read_gml('networkNLjunctions.gml')

# Plot the junction graph and the route

posDict = {}
for k in junctionGraph.nodes:
    posDict[k] = (junctionGraph.nodes[k]['x'], junctionGraph.nodes[k]['y'])

route_coords = np.array([posDict[r] for r in rt])

plt.figure(figsize=(10,10))
nx.draw(junctionGraph, pos=posDict, node_size=100, arrows=False)
plt.plot(route_coords[:,0], route_coords[:,1], 'r', linewidth=5)
plt.show()

    






################################
# The full network
################################


def linestring_destringizer(x):
    '''
    Takes string x and converts it to an object.
    In this case, only LineStrings will be converted.

    Parameters
    ----------
    x : str
        The string that will be converted.

    '''
    if x[0:10] == 'LINESTRING':  # convert to linestring
        s1 = x[12:-1].split(', ')
        pts = []
        for p in s1:
            pt = p.split(' ')
            pts.append((float(pt[0]),float(pt[1])))
        return LineString(pts)

    return str(x)


networkGraph = nx.read_gml('networkNLcomplete.gml', destringizer=linestring_destringizer)


posDict2 = {}
for k in networkGraph.nodes:
    posDict2[k] = (networkGraph.nodes[k]['x'], networkGraph.nodes[k]['y'])

plt.figure(figsize=(10,10))
nx.draw(networkGraph, pos=posDict2, node_size=0, arrows=False)
plt.show()


# compare the junctions on the route we studied earlier:
# 1. assignment graph
rt = nx.shortest_path(assignmentGraph,fromJunction,toJunction, weight='length')
print(rt)

# 2. full network graph
rt2 = nx.shortest_path(networkGraph,fromJunction,toJunction, weight='length')
print(rt2)










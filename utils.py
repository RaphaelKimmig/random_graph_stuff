from random import randint, choice
import math
import random

import networkx as nx
import pickle
from os import path
import sys

from algorithms import dijkstra

def print_header(name, n, m):
    head = "%32s | %12s | %21s | %21s" % ('algorithm', 'distance', 'settled', 'relaxed')
    
    print ''
    print "Graph: %s (vertices: %d, edges: %d)" % (name, n, m)
    print '-' * len(head)
    print head
    print '-' * len(head)
    sys.stdout.flush()

def print_result(name, res, base_result, n, m):

    d, _n, _m = res
    _, n, m = base_result
    print "%32s | %12.2f | %12d (%5.1f%%) | %12d (%5.1f%%)" %\
        (name, d, _n, 100 * float(_n)/n, _m, 100 * float(_m)/m) 
    sys.stdout.flush()


def build_graph(size=0, expected_neighbors=0, reverse_chance=0.9, min_weight=1, max_weight=3):
    """Build the graph

    Parameters:

    *size*
    The number of nodes to be in the graph
    *expected_neighbors*
    The expected degree of each node in the graph
    """

    # Calculate the distance required to yield the expected # neighbors
    if size == 1:
        radius = 1
    else:
        radius = math.sqrt( (expected_neighbors / (size - 1.0)) / math.pi)

    # Create bins in which to put node so we only check a fraction of
    # candidate neighbors
    num_bins = int(math.ceil(1/radius))
    neighbor_bins = []
    for i in range(num_bins):
        neighbor_bins.append([])
        for j in range(num_bins):
            neighbor_bins[i].append([])

    G = nx.DiGraph()
    G.name = "Nice Digraph"
    G.add_nodes_from(list(range(size)))

    # Create the collection of nodes and put them into bins with
    # candidate neighbors
    _rndm = random.random
    _rndint = random.randint
    _flr = math.floor
    for n in G.nodes():
        xcoord = _rndm()
        ycoord = _rndm()
        G.node[n]['coords'] = (xcoord, ycoord)

        # Put node into bin with candidate neighbors
        bin_x = int(_flr(xcoord/radius))
        bin_y = int(_flr(ycoord/radius))
        neighbor_bins[bin_x][bin_y].append(n)

    # Find actual neighbors and create edges between nodes
    for x in range(num_bins):
        for y in range(num_bins):

            # Get all potential neighbors (those in adjacent bins)
            potentials = []
            for px in range(x-1, x+1+1):
                if px < 0 or px >= num_bins:
                    continue

                for py in range(y-y, y+1+1):
                    if py < 0 or py >= num_bins:
                        continue

                    potentials += neighbor_bins[px % num_bins][py % num_bins]

            for node in neighbor_bins[x][y]:
                node_coords = G.node[node]['coords']
                for potential in potentials:
                    p_coords = G.node[potential]['coords']
                    dist = ((node_coords[0] - p_coords[0])**2 + (node_coords[1] - p_coords[1]) ** 2)**0.5
                    if dist < radius and node != potential:
                        weight = (min_weight + _rndm()* max_weight) * dist
                        G.add_edge(node, potential, weight=weight)
                        if _rndm() <= reverse_chance:
                            G.add_edge(potential, node, weight=weight)

                if G.degree(node) == 0:
                    G.remove_node(node)
                    neighbor_bins[x][y].remove(node)

            neighbor_bins[x][y] = []

    return G

def generate_g(file_name, nodes=10000):
    #seed = nx.generators.random_graphs.random_regular_graph(4, 80000)

    seed = build_graph(nodes, 8)

    edges = [ (u, v, data['weight'] * nodes) for (u, v, data) in seed.edges(data=True) ]
    g = nx.DiGraph()
    for (u, v, w) in edges:
        g.add_edge(u,v, weight=w)

    s = g.nodes()[0]
    cover, distances = dijkstra(g, s)
    t = choice(cover.nodes())

    reachable = dict((node, True) for node in cover.nodes())
    edges= [ (u, v, w) for (u,v,w) in edges if u in reachable and v in
            reachable ]
    nodes = [ (node, seed.node[node]['coords'][0] * nodes,
        seed.node[node]['coords'][1] * nodes) for node in cover.nodes() ]

    with open(file_name, 'a') as file:
        pickle.dump((nodes, edges, s), file)

def get_graph(name, size=10000):
    file_name = "graphs/graph_%s_%d" % (name, size)
    g = nx.DiGraph()
    # random.seed(5)

    if not path.exists(file_name):
        sys.stdout.write("generating ... ")
        sys.stdout.flush()
        generate_g(file_name, nodes=size)
        sys.stdout.write("done\n")
        sys.stdout.flush()

    with open(file_name) as file:
        sys.stdout.write("loading ... ")
        sys.stdout.flush()
        nodes, edges, s = pickle.load(file)
        sys.stdout.write("done\n")
        sys.stdout.flush()

    sys.stdout.write("constructing ... ")
    sys.stdout.flush()

    g.add_nodes_from(((node, {'x': x, 'y': y}) for (node, x, y) in nodes))
    for (u,v,w) in edges:
        g.add_edge(u,v, weight=w)
    n, m = len(g.nodes()), len(g.edges())

    sys.stdout.write("done\n")
    sys.stdout.flush()

    return g, n, m, s

def get_targets(g, s, ranks):
    _, distances = dijkstra(g, s)
    distances = distances.items()
    distances.sort(key=lambda (x,y): y)
    targets = [ (distances[r][0], r) for r in ranks]
    return targets

def draw(title, graph, s, ts, search_spaces=list()):
    from matplotlib import pylab
    fig = pylab.figure()

    fig.canvas.set_window_title(title)
    import matplotlib.pyplot as plt

    #pos = nx.graphviz_layout(graph, prog='dot')
    layout = dict(((node, (graph.node[node]['x'], graph.node[node]['y'])) for
        node in graph.nodes()))

    graph = nx.Graph(graph)
    nx.draw(graph, layout, node_color='white', with_labels=False, node_size=5)

    n_spaces = len(search_spaces)
    colors = [ 'r', 'g', 'b']
    for i, search_space in enumerate(search_spaces):
        print (1.0/n_spaces)*i, (1.0/n_spaces)*(i+1)
        b = len(search_space)
        nx.draw_networkx_nodes(graph, layout, nodelist=search_space, node_color=colors[i], node_size=150)

    nx.draw_networkx_nodes(graph, layout, nodelist=[s], node_color='cyan', node_size=50)

    nx.draw_networkx_nodes(graph, layout, nodelist=ts, node_color=range(len(ts), 0, -1), cmap=plt.cm.autumn, node_size=50)

#    edge_labels=dict([((u,v,),"%5.1f" % d['weight'])
#                 for u,v,d in graph.edges(data=True)])
#    nx.draw_networkx_edge_labels(graph, layout, edge_labels=edge_labels)



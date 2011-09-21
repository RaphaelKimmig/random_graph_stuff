from data import constant_factory, PriorityQueue
from collections import defaultdict
from networkx import nx

__all__ = ['dijkstra', 'dijkstra_cancel', 'dijkstra_bidirectional', 'dijkstra_bidirectional_mue']
def dijkstra(graph, s):
    distances = defaultdict(constant_factory(float("+inf")))
    parents = {}

    queue = PriorityQueue()
    queue.insert(s, 0)
    distances[s] = 0
    visited = 0
    while not queue.is_empty():
        u, k = queue.extract_min()
        visited += 1
        for node, edge_details in graph[u].items():
            if distances[u] + edge_details['weight'] < distances[node]:
                distances[node] = distances[u] + edge_details['weight']
                parents[node] = u
                if queue.contains(node):
                    queue.decrease_key(node, distances[node])
                else:
                    queue.insert(node, distances[node])
    result = nx.DiGraph()
    for u, v, data in graph.edges(data=True):
        if v in parents and parents[v] == u:
            result.add_edge(u, v, **data)
    return result, distances

def dijkstra_cancel(graph, s, t):
    distances = defaultdict(constant_factory(float("+inf")))
    parents = {}

    queue = PriorityQueue()
    queue.insert(s, 0)
    distances[s] = 0
    
    settled = 0
    relaxed = 0

    settled_nodes = []

    while not queue.is_empty():
        u, k = queue.extract_min()
        settled += 1
        settled_nodes.append(u)
        if u == t:
            break
        for node, edge_details in graph[u].items():
            if distances[u] + edge_details['weight'] < distances[node]:
                relaxed += 1
                distances[node] = distances[u] + edge_details['weight']
                parents[node] = u
                if queue.contains(node):
                    queue.decrease_key(node, distances[node])
                else:
                    queue.insert(node, distances[node])
    return distances[t], settled, relaxed, [settled_nodes]

def dijkstra_bidirectional(graph, s, t, cancel=False):
    graphr = graph.reverse(copy=True)
    distances = defaultdict(constant_factory(float("+inf")))
    distancesr = defaultdict(constant_factory(float("+inf")))

    queue = PriorityQueue()
    queue.insert(s, 0)

    queuer = PriorityQueue()
    queuer.insert(t, 0)

    distances[s] = 0
    distancesr[t] = 0

    mue = float("+inf")

    settled = {}

    num_settled = 0
    num_relaxed = 0

    settled_forward = []
    settled_backward = []
    while not queue.is_empty() and not queuer.is_empty():
        u, k = queue.extract_min()
        num_settled += 1
        for node, edge_details in graph[u].items():
            if distances[u] + edge_details['weight'] < distances[node]:
                num_relaxed += 1
                distances[node] = distances[u] + edge_details['weight']
                mue = min(mue, distances[node] + distancesr[node])
                if queue.contains(node):
                    queue.decrease_key(node, distances[node])
                else:
                    queue.insert(node, distances[node])
        settled_forward.append(u)
        if u in settled:
            break
        settled[u] = True


        ur, kr = queuer.extract_min()
        num_settled += 1
        for node, edge_details in graphr[ur].items():
            if distancesr[ur] + edge_details['weight'] < distancesr[node]:
                num_relaxed += 1
                distancesr[node] = distancesr[ur] + edge_details['weight']
                mue = min(mue, distances[node] + distancesr[node])
                if queuer.contains(node):
                    queuer.decrease_key(node, distancesr[node])
                else:
                    queuer.insert(node, distancesr[node])
        settled_backward.append(ur)
        if ur in settled:
            break
        settled[ur] = True


    return mue, num_settled, num_relaxed, [settled_forward, settled_backward]

def dijkstra_bidirectional_mue(graph, s, t, cancel=False):
    graphr = graph.reverse(copy=True)
    distances = defaultdict(constant_factory(float("+inf")))
    distancesr = defaultdict(constant_factory(float("+inf")))

    queue = PriorityQueue()
    queue.insert(s, 0)

    queuer = PriorityQueue()
    queuer.insert(t, 0)

    distances[s] = 0
    distancesr[t] = 0

    mue = float("+inf")


    num_settled = 0
    num_relaxed = 0

    while not queue.is_empty() and not queuer.is_empty():
        u, k = queue.extract_min()
        num_settled += 1
        for node, edge_details in graph[u].items():
            if distances[u] + edge_details['weight'] < distances[node]:
                num_relaxed += 1
                distances[node] = distances[u] + edge_details['weight']
                mue = min(mue, distances[node] + distancesr[node])
                if queue.contains(node):
                    queue.decrease_key(node, distances[node])
                else:
                    queue.insert(node, distances[node])

        ur, kr = queuer.extract_min()
        num_settled += 1
        for node, edge_details in graphr[ur].items():
            if distancesr[ur] + edge_details['weight'] < distancesr[node]:
                num_relaxed += 1
                distancesr[node] = distancesr[ur] + edge_details['weight']
                mue = min(mue, distances[node] + distancesr[node])
                if queuer.contains(node):
                    queuer.decrease_key(node, distancesr[node])
                else:
                    queuer.insert(node, distancesr[node])

        if k + kr > mue:
            break
    return mue, num_settled, num_relaxed

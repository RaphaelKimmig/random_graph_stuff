import random
from data import constant_factory, PriorityQueue
from collections import defaultdict
from dijkstra import dijkstra

__all__ = [ 'random_walker', 'cheater']

def random_walker(g, s, t):
    node = s
    visited = 0
    for i in xrange(2 * len(g.nodes()) ** 3):
        if node == t:
            return visited, 1, 1
        try:
            node = random.choice(g[node].keys())
        except IndexError:
            node = s
        visited += 1
    return visited, 0, 0

def cheater(graph, s, t):
    g_reverse = graph.reverse(copy=True)
    _, pi = dijkstra(g_reverse, t)

    distances = defaultdict(constant_factory(float("+inf")))
    parents = {}

    queue = PriorityQueue()
    queue.insert(s, pi[s])
    distances[s] = 0
    
    settled = 0
    relaxed = 0

    while not queue.is_empty():
        u, r = queue.extract_min()
        settled += 1
        if u == t:
            break
        for node, edge_details in graph[u].items():
            if distances[u] + edge_details['weight'] < distances[node]:
                relaxed += 1
                distances[node] = distances[u] + edge_details['weight']
                parents[node] = u
                if queue.contains(node):
                    queue.decrease_key(node, distances[node] + pi[node])
                else:
                    queue.insert(node, distances[node] + pi[node])
    return distances[t], settled, relaxed, [ parents.keys(), [] ]


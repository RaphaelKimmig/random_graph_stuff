from data import constant_factory, PriorityQueue
from collections import defaultdict

__all__ = ['a_star', 'a_star_bidirectional', 'a_star_bidirectional_betterpi', 'a_star_bidirectional_onesided']

def a_star(graph, s, t):
    xt, yt = graph.node[t]['x'], graph.node[t]['y']
    def pi(v):
        x, y = graph.node[v]['x'], graph.node[v]['y']
        return ((x - xt) **2 + (y - yt) ** 2) ** 0.5

    distances = defaultdict(constant_factory(float("+inf")))
    parents = {}

    queue = PriorityQueue()
    queue.insert(s, pi(s))
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
                    queue.decrease_key(node, distances[node] + pi(node))
                else:
                    queue.insert(node, distances[node] + pi(node))
    return distances[t], settled, relaxed, [settled_nodes]



def a_star_bidirectional(graph, s, t):
    """
    Bidirectional A* that stops iff one search has found the target
    """
    graphr = graph.reverse(copy=True)
    xt, yt = graph.node[t]['x'], graph.node[t]['y']
    def pi(v):
        x, y = graph.node[v]['x'], graph.node[v]['y']
        return ((x - xt) **2 + (y - yt) ** 2) ** 0.5

    xs, ys = graph.node[s]['x'], graph.node[s]['y']
    def pir(v):
        x, y = graph.node[v]['x'], graph.node[v]['y']
        return ((x - xs) **2 + (y - ys) ** 2) ** 0.5

    pf = lambda v : (pi(v) - pir(v))/2.0
    pr = lambda v : (pir(v) - pi(v))/2.0

    pfs = pf(s)
    pft = pf(t)

    distances = defaultdict(constant_factory(float("+inf")))
    distancesr = defaultdict(constant_factory(float("+inf")))

    queue = PriorityQueue()
    queue.insert(s, pi(s))

    queuer = PriorityQueue()
    queuer.insert(t, pir(t))

    distances[s] = 0
    distancesr[t] = 0

    mue = float("+inf")


    num_settled = 0
    num_relaxed = 0

    settled_nodes = []
    settled_nodes_r = []

    while not queue.is_empty() and not queuer.is_empty():
        u, k = queue.extract_min()
        num_settled += 1
        settled_nodes.append(u)
        if u == t:
            mue = distances[t]
            break
        for node, edge_details in graph[u].items():
            if distances[u] + edge_details['weight'] < distances[node]:
                num_relaxed += 1
                distances[node] = distances[u] + edge_details['weight']
                mue = min(mue, distances[node] + distancesr[node])
                if queue.contains(node):
                    queue.decrease_key(node, distances[node] + pf(node))
                else:
                    queue.insert(node, distances[node] + pf(node))

        ur, kr = queuer.extract_min()
        num_settled += 1
        settled_nodes_r.append(ur)
        if ur == s:
            mue = distancesr[s]
            break
        for node, edge_details in graphr[ur].items():
            if distancesr[ur] + edge_details['weight'] < distancesr[node]:
                num_relaxed += 1
                distancesr[node] = distancesr[ur] + edge_details['weight']
                mue = min(mue, distances[node] + distancesr[node])
                if queuer.contains(node):
                    queuer.decrease_key(node, distancesr[node] + pr(node))
                else:
                    queuer.insert(node, distancesr[node] + pr(node))

        if k + kr > mue + pfs - pft:
            break
    return mue, num_settled, num_relaxed, [settled_nodes, settled_nodes_r]
def a_star_bidirectional_betterpi(graph, s, t):
    """
    Bidirectional A* that stops iff one search has found the target
    """
    graphr = graph.reverse(copy=True)
    xt, yt = graph.node[t]['x'], graph.node[t]['y']
    xs, ys = graph.node[s]['x'], graph.node[s]['y']
    b = (yt - ys) / (xt - xs)
    bquer = - (1 / b)
    y0 = yt - b * xt
    s_t = lambda x: y0 + b * x
    def pi(v):
        x, y = graph.node[v]['x'], graph.node[v]['y']
        c = y - bquer * x
        xv = (y0 - c) / (bquer - b)
        yv = s_t(xv)
        return ((xv - xt) **2 + (yv - yt) ** 2) ** 0.5

    def pir(v):
        x, y = graph.node[v]['x'], graph.node[v]['y']
        c = y - bquer * x
        xv = (y0 - c) / (bquer - b)
        yv = s_t(xv)
        return ((xv - xs) **2 + (yv - ys) ** 2) ** 0.5

    pf = lambda v : (pi(v) - pir(v))/2.0
    pr = lambda v : (pir(v) - pi(v))/2.0


    settled_nodes = []
    settled_nodes_r = []

    pfs = pf(s)
    pft = pf(t)

    distances = defaultdict(constant_factory(float("+inf")))
    distancesr = defaultdict(constant_factory(float("+inf")))

    queue = PriorityQueue()
    queue.insert(s, pi(s))

    queuer = PriorityQueue()
    queuer.insert(t, pir(t))

    distances[s] = 0
    distancesr[t] = 0

    mue = float("+inf")


    num_settled = 0
    num_relaxed = 0

    while not queue.is_empty() and not queuer.is_empty():
        u, k = queue.extract_min()
        settled_nodes.append(u)
        num_settled += 1
        for node, edge_details in graph[u].items():
            if distances[u] + edge_details['weight'] < distances[node]:
                num_relaxed += 1
                distances[node] = distances[u] + edge_details['weight']
                mue = min(mue, distances[node] + distancesr[node])
                if queue.contains(node):
                    queue.decrease_key(node, distances[node] + pf(node))
                else:
                    queue.insert(node, distances[node] + pf(node))

        ur, kr = queuer.extract_min()
        settled_nodes_r.append(ur)
        num_settled += 1
        for node, edge_details in graphr[ur].items():
            if distancesr[ur] + edge_details['weight'] < distancesr[node]:
                num_relaxed += 1
                distancesr[node] = distancesr[ur] + edge_details['weight']
                mue = min(mue, distances[node] + distancesr[node])
                if queuer.contains(node):
                    queuer.decrease_key(node, distancesr[node] + pr(node))
                else:
                    queuer.insert(node, distancesr[node] + pr(node))


        if k + kr > mue + pfs - pft:
            break
    return mue, num_settled, num_relaxed, [settled_nodes, settled_nodes_r]

def a_star_bidirectional_onesided(graph, s, t):
    """
    Bidirectional A* that stops iff one search has found the target
    """
    graphr = graph.reverse(copy=True)
    xt, yt = graph.node[t]['x'], graph.node[t]['y']
    def pi(v):
        x, y = graph.node[v]['x'], graph.node[v]['y']
        return ((x - xt) **2 + (y - yt) ** 2) ** 0.5

    xs, ys = graph.node[s]['x'], graph.node[s]['y']
    def pir(v):
        x, y = graph.node[v]['x'], graph.node[v]['y']
        return ((x - xs) **2 + (y - ys) ** 2) ** 0.5

    distances = defaultdict(constant_factory(float("+inf")))
    distancesr = defaultdict(constant_factory(float("+inf")))

    queue = PriorityQueue()
    queue.insert(s, pi(s))

    queuer = PriorityQueue()
    queuer.insert(t, pir(t))

    distances[s] = 0
    distancesr[t] = 0

    mue = float("+inf")

    settled = {}

    num_settled = 0
    num_relaxed = 0

    while not queue.is_empty() and not queuer.is_empty():
        u, k = queue.extract_min()
        num_settled += 1
        if mue < k:
            break
        for node, edge_details in graph[u].items():
            if distances[u] + edge_details['weight'] < distances[node]:
                num_relaxed += 1
                distances[node] = distances[u] + edge_details['weight']
                mue = min(mue, distances[node] + distancesr[node])
                if queue.contains(node):
                    queue.decrease_key(node, distances[node] + pi(node))
                else:
                    queue.insert(node, distances[node] + pi(node))

        ur, kr = queuer.extract_min()
        num_settled += 1
        if mue < kr:
            break
        for node, edge_details in graphr[ur].items():
            if distancesr[ur] + edge_details['weight'] < distancesr[node]:
                num_relaxed += 1
                distancesr[node] = distancesr[ur] + edge_details['weight']
                mue = min(mue, distances[node] + distancesr[node])
                if queuer.contains(node):
                    queuer.decrease_key(node, distancesr[node] + pir(node))
                else:
                    queuer.insert(node, distancesr[node] + pir(node))
    return mue, num_settled, num_relaxed

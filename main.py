from _collections import defaultdict
import cProfile
from matplotlib import pylab
import pstats
import sys
import math
from utils import draw

from utils import get_graph, print_header, print_result, get_targets

from algorithms import *

if __name__ == '__main__':
    try:
        name = sys.argv[1]
    except IndexError:
        name = 'default'

    try:
        size = int(sys.argv[2])
    except IndexError, ValueError:
        size = 10000

    try:
        draw_it = sys.argv[3] == 'draw'
    except IndexError:
        draw_it = False


    try:
        draw_rank = int(sys.argv[4])
    except IndexError:
        draw_rank = size/2



    epsilon = 0.001

    g, n, m, s = get_graph(name, size=size)


    ts = get_targets(g, s, [ 2**i for i in xrange(4, int(math.log(n, 2))) if 2**i < n ])
    if draw_it:
        ts = get_targets(g, s, [draw_rank])
    algorithms = [ a_star_bidirectional ]      
#    algorithms = [ dijkstra_cancel, dijkstra_bidirectional, a_star, a_star_bidirectional  ]
#    algorithms = [ dijkstra_cancel, dijkstra_bidirectional, dijkstra_bidirectional_mue, a_star,
#                   a_star_bidirectional, a_star_bidirectional_onesided, a_star_bidirectional_betterpi, cheater ]
    results = defaultdict(list)
    base_results = []
    sys.stdout.write('running ')
    count = 0

    # for t, rank in ts:
    #     rd = dijkstra_cancel(g, s, t)
    #     ra = a_star(g, s, t)

    #     highlight = []
    #     highlight.extend(rd[3])
    #     highlight.extend(ra[3])
    #     draw('zwei', g, s, [t for (t,r) in ts], highlight)
    #     pylab.show()
    #     sys.exit(0)


    for t, rank in ts:
        base_results.append(dijkstra_cancel(g, s, t))
        for algorithm in algorithms:
            result = algorithm(g, s, t)
            results[algorithm].append(result)
            if draw_it:
                if len(result) >= 4:
                    search_spaces = result[3]
                    if len(search_spaces) == 2:
                        both = set(search_spaces[0]).intersection(set(search_spaces[1]))
                        search_spaces.append(both)
                else:
                    search_spaces = []
                draw(algorithm.__name__, g, s, [t for (t,r) in ts], search_spaces)
                count += 1
            sys.stdout.write('.')
            sys.stdout.flush()
    sys.stdout.write(' done\n')



    sys.stdout.write("%32s |" % "t")
    for (t, rank) in ts:
        sys.stdout.write("%11d |" % rank)
    sys.stdout.write('\n')
    sys.stdout.write('-' * (34 + len(ts) * 13))
    sys.stdout.write('\n')

    errors = []
    for algorithm in algorithms:
        sys.stdout.write("%32s |" % algorithm.__name__)
        for i, target in enumerate(ts):
            d, n, m = results[algorithm][i][0:3]
            db, nb, mb = base_results[i][0:3]
            if abs(d - db) > epsilon:
                sys.stdout.write("%11s |" % "error")
                errors.append((algorithm, results[algorithm][i], base_results[i], target))
            else:
                sys.stdout.write("%5.1f %5.1f |" % (float(nb)/n, float(mb)/m))
        sys.stdout.write('\n')
    sys.stdout.flush()

    for algorithm, results, base_results, target in errors:
        d = results[0]
        db = base_results[0]
        print "error in algorithm %s, rank %d: result was %f (correct: %f)" % (algorithm.__name__, target[1], d, db)
    #            print_header(name, n, m)

    #     res = dijkstra_cancel(g, s, t)
    #     print_result("normal", res, n, m)

#
#        base_result = dijkstra_cancel(g, s, t)
#        print_result("dijkstra", base_result, base_result, n, m)
#
#        res = dijkstra_bidirectional(g, s, t)
#        print_result("dijkstra bidirectional", res, base_result, n, m)
#
#        res = dijkstra_bidirectional_mue(g, s, t)
#        print_result("dijkstra bidirectional mue", res, base_result, n, m)
#
#        res = a_star(g, s, t)
#        print_result("A*", res, base_result, n, m)
#
#        res = a_star_bidirectional_onesided(g, s, t)
#        print_result("A* bidirectional onesided", res, base_result, n, m)
#
#        res = a_star_bidirectional(g, s, t)
#        print_result("A* bidirectional", res, base_result, n, m)
#
#        res = cheater(g, s, t)
#        print_result("cheater", res, base_result, n, m)
#
#        # cProfile.run("dijkstra_cancel(g, s, t)", 'dijkstra')
#        # p_classic = pstats.Stats('dijkstra')
#        # p_classic.sort_stats('time').print_stats()
#

    if draw_it:
        from matplotlib import pylab
        pylab.show()

import networkx as nx
import itertools
import random
from collections import deque
from queue import PriorityQueue
from collections import defaultdict


def _check_params(G, strategy, opt_alg, it_limit, verbose):
    greedy_methods = {"random", "welsh_powell", "dsatur", "rlf"}
    opt_methods = {1, 2, 3, 4, 5, None}
    if strategy not in greedy_methods:
        raise ValueError(
            "Error, chosen strategy must be one of", greedy_methods
        )
    if opt_alg not in opt_methods:
        raise ValueError(
            "Error, chosen optimisation method must be one of", opt_methods
        )
    if not isinstance(it_limit, int) or it_limit < 0:
        raise ValueError(
            "Error, it_limit parameter must be a non-negative integer"
        )
    if not isinstance(verbose, int) or verbose < 0:
        raise ValueError(
            "Error, verbose parameter must be a non-negative integer"
        )
    if G.is_directed() or G.is_multigraph():
        raise NotImplementedError(
            "Error, this method cannot be used with directed graphs or "
            "multigraphs"
        )
    if nx.number_of_selfloops(G) != 0:
        raise NotImplementedError(
            "Error, this method cannot be used with graphs featuring "
            "self-loops (edges of the form {u, u})"
        )


def _getNodeWeights(G, weight):
    # Puts all node weights into a dict W
    W = {}
    for u in G:
        if weight is None:
            W[u] = 1
        else:
            try:
                W[u] = G.nodes[u][weight]
            except KeyError:
                raise ValueError(
                    "Error, all nodes must feature the property", weight
                )
            if W[u] <= 0:
                raise ValueError("Error, all node weights must be positive")
    return W


def _getEdgeWeights(G, weight):
    # Puts all edge weights into a dict
    W = {}
    for u in G:
        for v in G[u]:
            if weight is None:
                W[u, v] = 1
            else:
                try:
                    W[u, v] = G[u][v][weight]
                except KeyError:
                    raise ValueError(
                        "Error, all edges must feature the property", weight
                    )
                if W[u, v] <= 0:
                    raise ValueError("Error, all edge weights must be postive")
    return W


def _LS_equitable(G, c, k, W, verbose):
    def getKempeChain(A, c, s, i, j):
        status = {s: 1}
        Q = deque([s])
        Chain = set()
        while Q:
            u = Q[0]
            if c[u] == i:
                colv = j
            else:
                colv = i
            for v in A[u, colv]:
                if v not in status:
                    status[v] = 1
                    Q.append(v)
            Q.popleft()
            status[u] = 2
            Chain.add(u)
        return Chain

    def evaluateKempeMove(c, Chain, i, j):
        for v in Chain:
            if c[v] == i:
                ColWeight[i] -= W[v]
                ColWeight[j] += W[v]
            elif c[v] == j:
                ColWeight[j] -= W[v]
                ColWeight[i] += W[v]
        newCost = (sum((x - mean) ** 2 for x in ColWeight) /
                   len(ColWeight)) ** 0.5
        for v in Chain:
            if c[v] == i:
                ColWeight[i] += W[v]
                ColWeight[j] -= W[v]
            elif c[v] == j:
                ColWeight[j] += W[v]
                ColWeight[i] -= W[v]
        return newCost

    def doKempeMove(c, Chain, i, j):
        for v in Chain:
            if c[v] == i:
                c[v] = j
                ColWeight[i] -= W[v]
                ColWeight[j] += W[v]
                ColCard[i] -= 1
                ColCard[j] += 1
            elif c[v] == j:
                c[v] = i
                ColWeight[j] -= W[v]
                ColWeight[i] += W[v]
                ColCard[j] -= 1
                ColCard[i] += 1

    def evaluateSwapMove(c, u, v):
        ColWeight[c[u]] += W[v] - W[u]
        ColWeight[c[v]] += W[u] - W[v]
        newCost = (sum((x - mean) ** 2 for x in ColWeight) /
                   len(ColWeight)) ** 0.5
        ColWeight[c[u]] += W[u] - W[v]
        ColWeight[c[v]] += W[v] - W[u]
        return newCost

    def doSwapMove(c, u, v):
        ColWeight[c[u]] += W[v] - W[u]
        ColWeight[c[v]] += W[u] - W[v]
        c[u], c[v] = c[v], c[u]

    # Main local search procedure for improving the balancing of each color
    # class. This uses steepest descent and halts at the first observed local
    # optimum
    if k <= 1:
        return c
    ColWeight = [0 for i in range(k)]
    ColCard = [0 for i in range(k)]
    for v in c:
        ColWeight[c[v]] += W[v]
        ColCard[c[v]] += 1
    mean = sum(x for x in ColWeight) / len(ColWeight)
    currentCost = (sum((x - mean) ** 2 for x in ColWeight) /
                   len(ColWeight)) ** 0.5
    if verbose > 0:
        print("Running equitable local search algorithm using", k, "colors:")
    V = list(G)
    while True:
        # Initialise data structures. KCRec[v,j] holds the size of the Kempe
        # chain formed by node v and color j (once calculated). A[v,j] gives a
        # list of all neighbours of v assigned to color j. These allow all
        # possible Kempe chains to be evaluated in O(vk + m) time
        KCRec = {v: [0 for j in range(k)] for v in G}
        A = {(v, j): [] for v in G for j in range(k)}
        for u in G:
            for v in G[u]:
                A[u, c[v]].append(v)
        bestVal = currentCost
        if verbose > 0:
            print("    Found solution with cost (std. dev.)", currentCost)
        for v in G:
            i = c[v]
            for j in range(k):
                if i != j:
                    if KCRec[v][j] == 0:
                        # Kempe-Chain(v,i,j) not yet observed, so handle it
                        Chain = getKempeChain(A, c, v, i, j)
                        for u in Chain:
                            if c[u] == i:
                                KCRec[u][j] = len(Chain)
                            else:
                                KCRec[u][i] = len(Chain)
                        if len(Chain) != ColCard[i] + ColCard[j]:
                            neighborCost = evaluateKempeMove(c, Chain, i, j)
                            if neighborCost < bestVal:
                                bestVal, bestv, besti, bestj, moveType = (
                                    neighborCost,
                                    v,
                                    i,
                                    j,
                                    1,
                                )
        # Now check all possible non-adjacent swaps. This takes O(n^2) time
        for i in range(len(V) - 1):
            for j in range(i + 1, len(V)):
                u, v = V[i], V[j]
                if (
                    c[u] != c[v]
                    and W[u] != W[v]
                    and KCRec[u][c[v]] == 1
                    and KCRec[v][c[u]] == 1
                ):
                    # Swapping u and v changes the cost and maintains
                    # feasibility
                    neighborCost = evaluateSwapMove(c, u, v)
                    if neighborCost < bestVal:
                        bestVal, bestu, bestv, moveType = neighborCost, u, v, 2
        if bestVal == currentCost:
            break
        if moveType == 1:
            Chain = getKempeChain(A, c, bestv, besti, bestj)
            doKempeMove(c, Chain, besti, bestj)
        else:
            doSwapMove(c, bestu, bestv)
        currentCost = bestVal
    if verbose > 0:
        print("Ending equitable local search algorithm - local optimum",
              "achieved.")
    return c


def _dsatur_equitable(G, k, W):
    # Version of DSatur algorithm that seeks to balance the color class sizes.
    # First initialise the data structures for this heuristic.
    # These are a priority queue q; the colors of each node c[v];
    # the set of colors adjacent to each uncolored node (initially empty
    # sets); the degree d[v] of each uncolored node in the graph induced
    # by uncolored nodes; and the weight of each color class.
    q = PriorityQueue()
    c, adjcols, d = {}, {}, {}
    colweight = [0 for i in range(k)]
    counter = itertools.count()
    for u in G.nodes:
        d[u] = G.degree(u)
        adjcols[u] = set()
        q.put((0, d[u] * (-1), next(counter), u))
    while len(c) < len(G):
        # Get the uncolored node u with max saturation degree, breaking
        # ties using the highest value for d. Remove u from q.
        _, _, _, u = q.get()
        if u not in c:
            # node u has not yet been colored, so assign it to the feasible
            # color class i that currently has the lowest weight
            i, mincolweight = None, float("inf")
            for j in range(k):
                if j not in adjcols[u] and colweight[j] < mincolweight:
                    i = j
                    mincolweight = colweight[i]
            if i is None:
                # A k-coloring could not be achieved by this heuristic so quit
                return None
            c[u] = i
            colweight[i] += W[u]
            # Update the saturation degrees and d-values of the uncolored
            # neighbors v, and update the priority queue q
            for v in G[u]:
                if v not in c:
                    adjcols[v].add(i)
                    d[v] -= 1
                    q.put((len(adjcols[v]) * (-1), d[v]
                          * (-1), next(counter), v))
    return c


def _greedy(G, V):
    # Greedy algorithm for graph coloring. This considers nodes of G in the
    # order given in V
    c = {}
    for u in V:
        adjcols = {c[v] for v in G[u] if v in c}
        for j in itertools.count():
            if j not in adjcols:
                break
        c[u] = j
    return c


def _dsatur(G, c=None):
    # Dsatur algorithm for graph coloring. First initialise the data
    # structures. These are: the colors of each node c[v]; the degree d[v] of
    # each uncolored node in the graph induced by uncolored nodes; the set of
    # colors adjacent to each uncolored node (initially empty sets); and a
    # priority queue q. In q, each element has 4 values for the node v. The
    # first two are the the saturation degree of v, d[v] (as a tie breaker).
    # The third value is a counter, which just stops comparisons being made
    # with the final values, which might be of different types.
    d, adjcols, q = {}, {}, PriorityQueue()
    counter = itertools.count()
    for u in G.nodes:
        d[u] = G.degree(u)
        adjcols[u] = set()
        q.put((0, d[u] * (-1), next(counter), u))
    # If any nodes are already colored in c, update the data structures
    # accordingly
    if c is not None:
        if not isinstance(c, dict):
            raise TypeError(
                "Error, c should be a dict that assigns a subset of nodes ",
                "to colors"
            )
        for u in c:
            for v in G[u]:
                if v not in c:
                    adjcols[v].add(c[u])
                    d[v] -= 1
                    q.put((len(adjcols[v]) * (-1), d[v]
                          * (-1), next(counter), v))
                elif c[u] == c[v]:
                    raise ValueError(
                        "Error, clashing nodes defined in supplied coloring"
                    )
    else:
        c = {}
        # Color all remaining nodes
    while len(c) < len(G):
        # Get the uncolored node u with max saturation degree, breaking ties
        # using the highest value for d. Remove u from q.
        _, _, _, u = q.get()
        if u not in c:
            # Get lowest color label i for uncolored node u
            for i in itertools.count():
                if i not in adjcols[u]:
                    break
            c[u] = i
            # Update the data structures
            for v in G[u]:
                if v not in c:
                    adjcols[v].add(i)
                    d[v] -= 1
                    q.put((len(adjcols[v]) * (-1), d[v]
                          * (-1), next(counter), v))
    return c


def _rlf(G):
    def update_rlf(u):
        # Remove u from X (it has been colored) and move all uncolored
        # neighbors of u from X to Y
        X.remove(u)
        for v in G[u]:
            if v not in c:
                X.discard(v)
                Y.add(v)
        # Recalculate the contets of NInX and NInY. First calculate a set D2
        # of all uncolored nodes within distance two of u.
        D2 = set()
        for v in G[u]:
            if v not in c:
                D2.add(v)
                for w in G[v]:
                    if w not in c:
                        D2.add(w)
        # For each node v in D2, recalculate the number of (uncolored)
        # neighbors in X and Y
        for v in D2:
            NInX[v] = 0
            NInY[v] = 0
            for w in G[v]:
                if w not in c:
                    if w in X:
                        NInX[v] += 1
                    elif w in Y:
                        NInY[v] += 1

    # RLF algorithm for graph coloring. Here, X is the set of uncolored nodes
    # not adjacent to any nodes colored with color i, and Y is the set of
    # uncolored nodes that are adjcent to nodes colored with i.
    c, Y, n, i = {}, set(), len(G), 0
    X = set(G.nodes())
    while X:
        # Construct color class i. First, for each nodes u in X, calculate the
        # number of neighbors it has in X and Y
        NInX, NInY = {u: 0 for u in X}, {u: 0 for u in X}
        for u in X:
            for v in G[u]:
                if v in X:
                    NInX[u] += 1
        # Identify and colur the uncolored node u in X that has the most
        # neighbors in X
        maxVal = -1
        for v in X:
            if NInX[v] > maxVal:
                maxVal, u = NInX[v], v
        c[u] = i
        update_rlf(u)
        while X:
            # Identify and color the node u in X that has the largest number
            # of neighbors in Y. Break ties according to the min neighbors in X
            mxVal, mnVal = -1, n
            for v in X:
                if NInY[v] > mxVal or (NInY[v] == mxVal and NInX[v] < mnVal):
                    mxVal, mnVal, u = NInY[v], NInX[v], v
            c[u] = i
            update_rlf(u)
        # Have finished constructing color class i
        X, Y = Y, X
        i += 1
    return c


def _backtrackcol(G, targetcols, verbose):
    def is_feasible(u, i):
        # Returns true iff node u can be feasibly assigned to color i in c
        for v in G[u]:
            if c.get(v) == i:
                return False
        return True

    def color(uPos):
        # Recursive function used for backtracking. Attempts to color node at
        # position uPos in V
        its[0] += 1
        if len(colsize) > numcols[0]:
            # Current (partial) solution is using too many colors, so backtrack
            return False
        if uPos == len(G):
            # At a leaf node in search tree. A new best solution has been
            # found.
            bestc.clear()
            for v in c:
                bestc[v] = c[v]
            if verbose > 0:
                print("    Found solution with", len(colsize),
                      "colors. Total backtracking iterations =", its[0])
            if len(colsize) == targetcols:
                # Optimum solution has been constructed or target reached
                return True
            else:
                # Reduce number of available colors and continue
                numcols[0] = len(colsize) - 1
                return False
        u = V[uPos]
        for i in range(numcols[0]):
            if i < numcols[0] and is_feasible(u, i):
                c[u] = i
                colsize[i] += 1
                if color(uPos + 1):
                    return True
                colsize[c[u]] -= 1
                if colsize[c[u]] == 0:
                    del colsize[c[u]]
                del c[u]
        return False

    # Exact backtracking algorithm for node coloring. First, find a large
    # clique C in G
    C = list(nx.approximation.max_clique(G))
    targetcols = max(targetcols, len(C))
    if verbose > 0:
        print("Running backtracking algorithm:")
    # Generate an initial solution. Do this by assigning the nodes in C
    # to different colors, then get a starting number of colors (numcols) using
    # dsatur. V holds the order in which the vetices were colored
    bestc = {C[i]: i for i in range(len(C))}
    bestc = _dsatur(G, bestc)
    numcols = [max(bestc.values()) + 1]
    if verbose > 0:
        print("    Found solution with",
              numcols[0], "colors. Total backtracking iterations = 0")
    numcols[0] -= 1
    V = list(bestc)
    # Now assign the nodes in C to c and run the backtracking algorithm
    # from the next node in V. Here, bestc holds the best solution seen so far
    # and colsize holds the size of all nonempty color classes in c.
    # len(colsize) therefore gives the number of colors (cost) being used by
    # the (sub-)solution c
    c, colsize, its = {}, defaultdict(int), [0]
    for i in range(len(C)):
        c[C[i]] = i
        colsize[i] += 1
    color(len(C))
    if verbose > 0:
        print("Ending backtracking at iteration",
              its[0], "- optimal solution achieved.")
    return bestc


def _partialcol(G, k, c, W, it_limit, verbose):
    def domovepartialcol(v, j):
        # Used by partialcol to move node v to color j and update relevant
        # data structures
        c[v] = j
        U.remove(v)
        for u in G[v]:
            C[u, j] += W[v]
            if c[u] == j:
                T[u, j] = its + t
                U.add(u)
                c[u] = -1
                for w in G[u]:
                    C[w, j] -= W[u]

    # Use the current solution c to populate the data structures. C[v,j] gives
    # the total weight of the neighbors of v in color j, T is the tabu list,
    # and U is the set of clashing nodes
    assert k >= 1, "Error, partialcol only works with at least k = 1 color"
    C, T, U, its = {}, {}, set(), 0
    for v in G:
        assert (
            isinstance(c[v], int) and c[v] >= -1 and c[v] < k
        ), ("Error, the coloring defined by c must allocate each node a ",
            "value from the set {-1,0,...,k-1}, where -1 signifies that ",
            "a node is uncolored")
        for j in range(k):
            C[v, j] = 0
            T[v, j] = 0
    for v in G:
        if c[v] == -1:
            U.add(v)
        for u in G[v]:
            if c[u] != -1:
                C[v, c[u]] += W[u]
    currentcost = sum(W[u] for u in U)
    bestcost, bestsol, t = float("inf"), {}, 1
    if verbose > 0:
        print("    Running PartialCol algorithm using", k, "colors")
    while True:
        # Keep track of best solution and halt when appropriate
        if currentcost < bestcost:
            if verbose > 0:
                print("        Solution with", k, "colors and cost",
                      currentcost, "found by PartialCol at iteration", its)
            bestcost = currentcost
            bestsol = dict(c)
        if bestcost <= 0 or its >= it_limit:
            break
        # Evaluate all neighbors of current solution c
        its += 1
        vbest, jbest, bestval, numbestval = -1, -1, float("inf"), 0
        for v in U:
            for j in range(k):
                neighborcost = currentcost + C[v, j] - W[v]
                if neighborcost <= bestval:
                    if neighborcost < bestval:
                        numbestval = 0
                    # Consider the move if it is not tabu or leads to a new
                    # best solution
                    if T[v, j] < its or neighborcost < bestcost:
                        if random.randint(0, numbestval) == 0:
                            vbest, jbest, bestval = v, j, neighborcost
                        numbestval += 1
        # Do the chosen move. If no move was chosen (all moves are tabu),
        # choose a random move
        if vbest == -1:
            vbest = random.choice(tuple(U))
            jbest = random.randint(0, k - 1)
            bestval = currentcost + C[vbest, jbest] - W[vbest]
        # Apply the move, update T, and determine the next tabu tenure t
        domovepartialcol(vbest, jbest)
        currentcost = bestval
        t = int(0.6 * len(U)) + random.randint(0, 9)
    if verbose > 0:
        print("    Ending PartialCol")
    return bestcost, bestsol, its


def _tabucol(G, k, c, W, it_limit, verbose):
    def domovetabucol(v, j):
        # Used by tabucol to move node v to a new color j and update relevant
        # data structures
        i = c[v]
        c[v] = j
        if C[v, i] > 0 and C[v, j] == 0:
            U.remove(v)
        elif C[v, i] == 0 and C[v, j] > 0:
            U.add(v)
        for u in G[v]:
            C[u, i] -= W[v, u]
            if C[u, i] == 0 and c[u] == i:
                U.remove(u)
            C[u, j] += W[v, u]
            if C[u, j] > 0 and c[u] == j:
                U.add(u)
        T[v, i] = its + t

    assert k >= 2, "Error, tabucol only works with at least k = 2 colors"
    # Use the current solution c to populate the data structures. C[v,j] gives
    # the number of neighbors of v in color j, T is the tabu list, and U is the
    # set of clashing nodes
    C, T, U, its, currentcost = {}, {}, set(), 0, 0
    for v in G:
        assert isinstance(c[v], int) and c[v] >= 0 and c[v] < k, (
            "Error, the coloring defined by c must allocate each node a ",
            "value from the set {0,...,k-1}"
            + str(v)
            + " "
            + str(c[v])
        )
        for j in range(k):
            C[v, j] = 0
            T[v, j] = 0
    for v in G:
        for u in G[v]:
            C[v, c[u]] += W[v, u]
    for v in G:
        if C[v, c[v]] > 0:
            currentcost += C[v, c[v]]
            U.add(v)
    currentcost //= 2
    bestcost, bestsol, t = float("inf"), {}, 1
    if verbose > 0:
        print("    Running TabuCol algorithm using", k, "colors")
    while True:
        # Keep track of best solution and halt when appropriate
        if currentcost < bestcost:
            if verbose > 0:
                print("        Solution with", k, "colors and cost",
                      currentcost, "found by TabuCol at iteration", its)
            bestcost = currentcost
            bestsol = dict(c)
        if bestcost <= 0 or its >= it_limit:
            break
        # Evaluate all neighbors of current solution
        its += 1
        vbest, jbest, bestval, numbestval = -1, -1, float("inf"), 0
        for v in U:
            for j in range(k):
                if j != c[v]:
                    neighborcost = currentcost + C[v, j] - C[v, c[v]]
                    if neighborcost <= bestval:
                        if neighborcost < bestval:
                            numbestval = 0
                        # Consider the move if it is not tabu or leads to a new
                        # global best
                        if T[v, j] < its or neighborcost < bestcost:
                            if random.randint(0, numbestval) == 0:
                                vbest, jbest, bestval = v, j, neighborcost
                            numbestval += 1
        # Do the chosen move. If no move was chosen (all moves are tabu),
        # choose a random move
        if vbest == -1:
            vbest = random.choice(tuple(c))
            while True:
                jbest = random.randint(0, k - 1)
                if jbest != c[vbest]:
                    break
            bestval = currentcost + C[vbest, jbest] - C[vbest, c[vbest]]
        domovetabucol(vbest, jbest)
        currentcost = bestval
        t = int(0.6 * len(U)) + random.randint(0, 9)
    if verbose > 0:
        print("    Ending TabuCol")
    return bestcost, bestsol, its


def _HEA(G, k, c, W, it_limit, verbose, doTabuCol):
    def choosecolor(S):
        # Used in GPX recombination operator. Returns the index of the largest
        # set (color class) in the partition S, breaking ties randomly
        maxCard, A = 0, []
        for i in range(len(S)):
            if len(S[i]) > 0:
                if len(S[i]) > maxCard:
                    A.clear()
                    A.append(i)
                    maxCard = len(S[i])
                elif len(S[i]) == maxCard:
                    A.append(i)
        if len(A) == 0:
            return -1
        else:
            return random.choice(A)

    def colornodes(off, i, col, P1, S1, P2, S2):
        # Used in GPX recombination operator. Removes color class col from P1
        # and S1, the same nodes from P2 and S2, and, in off, assigns these
        # nodes to color i
        for u in S1[col]:
            P1[u] = -1
            if P2[u] != -1:
                S2[P2[u]].remove(u)
                P2[u] = -1
            off[u] = i
        S1[col].clear()

    def GPX(parent1, parent2):
        # Makes copies (P1 and P2) of the two parents, creates corresponding
        # partitons S1 and S2, and uses these to create the offspring off
        P1, P2 = dict(parent1), dict(parent2)
        S1, S2 = [set() for i in range(k)], [set() for i in range(k)]
        off = {u: -1 for u in G}
        for u in G:
            if P1[u] != -1:
                S1[P1[u]].add(u)
            if P2[u] != -1:
                S2[P2[u]].add(u)
        for i in range(k):
            if i % 2 == 0:
                # Copy a color class from first parent to the offspring
                col = choosecolor(S1)
                if col != -1:
                    colornodes(off, i, col, P1, S1, P2, S2)
            else:
                # Copy a color class from second parent to the offspring
                col = choosecolor(S2)
                if col != -1:
                    colornodes(off, i, col, P2, S2, P1, S1)
        if doTabuCol:
            # Assign any remaining uncolored nodes randomly
            for u in P1:
                if off[u] == -1:
                    off[u] = random.randint(0, k - 1)
        return off

    # Implementation of the HEA for graph k-coloring
    if doTabuCol:
        for v in G:
            assert isinstance(c[v], int) and c[v] >= 0 and c[v] < k, (
                "Error, the coloring defined by c must allocate each node a ",
                "value from the set {0,...,k-1}"
                + str(v)
                + " "
                + str(c[v])
            )
    else:
        for v in G:
            assert (
                isinstance(c[v], int) and c[v] >= -1 and c[v] < k
            ), ("Error, the coloring defined by c must allocate each node a ",
                "value from the set {-1,0,...,k-1}, where -1 signifies that ",
                "a node is uncolored")
    popsize, itsperindv, totalits = min(10, len(G)), 16 * len(G), 0
    bestcost, bestsol = float("inf"), {}
    # Create the initial population. The first individual is found by applying
    # local search to c; the remainder by applying dsatur with a randomly
    # selected initial node, then applying local search.
    if verbose > 0:
        print("    Making HEA initial solution 1 using", k, "colors")
    if doTabuCol:
        cost, c, its = _tabucol(G, k, c, W, min(
            itsperindv, it_limit - totalits), verbose)
    else:
        cost, c, its = _partialcol(G, k, c, W, min(
            itsperindv, it_limit - totalits), verbose)
    totalits += its
    if cost < bestcost:
        bestcost, bestsol = cost, dict(c)
    if cost == 0 or totalits >= it_limit:
        return bestcost, bestsol, totalits
    pop, popcost = [c], [cost]
    randomnodes = random.sample(list(G.nodes), popsize - 1)
    for i in range(0, popsize - 1):
        if verbose > 0:
            print("    Making HEA initial solution", i + 2,
                  "using", k, "colors")
        sol = {randomnodes[i]: 0}
        sol = _dsatur(G, sol)
        if doTabuCol:
            for u in sol:
                if sol[u] >= k:
                    sol[u] = random.randint(0, k - 1)
            cost, sol, its = _tabucol(G, k, sol, W, min(
                itsperindv, it_limit - totalits), verbose)
        else:
            for u in sol:
                if sol[u] >= k:
                    sol[u] = -1
            cost, sol, its = _partialcol(G, k, sol, W, min(
                itsperindv, it_limit - totalits), verbose)
        totalits += its
        if cost < bestcost:
            bestcost, bestsol = cost, dict(sol)
        if cost == 0 or totalits >= it_limit:
            return bestcost, bestsol, totalits
        pop.append(sol)
        popcost.append(cost)
    # At this point we have not found a zero-cost solution so we apply the main
    # part of the HEA, evolving the population of individual solutions
    i = 1
    while True:
        # Choose two parents, make the offspring, and apply local search
        p1, p2 = random.sample(range(popsize), 2)
        if verbose > 0:
            print("    Making HEA offspring", i, "using", k, "colors")
        off = GPX(pop[p1], pop[p2])
        if doTabuCol:
            cost, off, its = _tabucol(G, k, off, W, min(
                itsperindv, it_limit - totalits), verbose)
        else:
            cost, off, its = _partialcol(G, k, off, W, min(
                itsperindv, it_limit - totalits), verbose)
        totalits += its
        if cost < bestcost:
            bestcost, bestsol = cost, dict(off)
        if cost == 0 or totalits >= it_limit:
            break
        # Replace the weaker of the parents with the new offspring solution
        weaker = p1
        if popcost[p2] > popcost[p1]:
            weaker = p2
        pop[weaker], popcost[weaker] = off, cost
        i += 1
    return bestcost, bestsol, totalits


def _removeColor(c, j, alg):
    maxcol = max(c.values())
    # Uncolor nodes assigned to color j while maintaining use of colors
    # 0,1,...,maxcol-1
    for v in c:
        if c[v] == j:
            c[v] = -1
        elif c[v] == maxcol:
            c[v] = j
    # If tabucol is being used, assign uncolored nodes to random colors
    if alg in [2, 4]:
        for v in c:
            if c[v] == -1:
                c[v] = random.randint(0, maxcol - 1)


def _reducecolors(G, c, target, W, opt_alg, it_limit, verbose):
    # Uses the specified optimization algorithm to try to reduce the number of
    # colors in c to the target value. The observed proper solution with the
    # fewest colors is returned (which may be using more colors than the
    # target)
    k = max(c.values()) + 1
    if opt_alg == 1:
        return _backtrackcol(G, target, verbose)
    bestc, totalits = dict(c), 0
    if verbose > 0:
        print("Running local search algorithm:")
        print("    Found solution with", k,
              "colors. Total local search iterations = 0 /", it_limit)
    while k > target and totalits < it_limit:
        k -= 1
        j = random.randint(0, k - 1)
        _removeColor(c, j, opt_alg)
        if opt_alg == 2:
            cost, c, its = _tabucol(
                G, k, c, W, it_limit - totalits, verbose - 1)
        elif opt_alg == 3:
            cost, c, its = _partialcol(
                G, k, c, W, it_limit - totalits, verbose - 1)
        elif opt_alg == 4:
            cost, c, its = _HEA(
                G, k, c, W, it_limit - totalits, verbose - 1, True)
        else:
            cost, c, its = _HEA(
                G, k, c, W, it_limit - totalits, verbose - 1, False)
        totalits += its
        if cost == 0:
            bestc = dict(c)
            if verbose > 0:
                print("    Found solution with", k,
                      "colors. Total local search iterations =", totalits,
                      "/", it_limit)
    if verbose > 0:
        if totalits >= it_limit:
            print("Ending local search. Iteration limit of",
                  it_limit, "has been reached.")
        else:
            print("Ending local search at iteration", totalits,
                  "- optimal solution achieved.")
    return bestc


def s_chain(G, c, v, L):
    """Return the set of nodes in an $s$-chain.

    An $s$-chain is a generalisation of a Kempe chain that allows more than two
    colors. Given a proper node coloring of a graph $G=(V,E)$, an $s$-chain is
    defined by a prescribed node $v\\in V$ and sequence of unique colors
    $j_0,j_1,\\ldots,j_{s-1}$, where the current color of $v$ is $j_0$. The
    result is the set of nodes that are reachable from $v$ in the digraph
    $G'=(V',A)$ in which:

    * $V' = \\{u \\; : \\; u \\in V \\; \\wedge \\; c(u) \\in \\{j_0,j_1,
      \\ldots,j_{s-1}\\}\\}$, and

    * $A = \\{(u,w) \\; : \\; \\{u,w\\} \\in E \\; \\wedge \\; c(u) = j_i \\;
      \\wedge \\; c(w) = j_{(i+1) \\bmod s} \\}$,

    where $c(u)$ gives the color of a node $u$.

    In a proper coloring, interchanging the colors of all nodes in an $s$-chain
    via the following mapping

    * $j_i \\leftarrow j_{(i+1) \\bmod s}$

    results in a new proper coloring [1]_.

    In this method, uncolored nodes are ignored.

    Parameters
    ----------
    G : NetworkX graph
        The graph that we want to compute an $s$-chain for.

    c : dict
        A node coloring of ``G``, where ``c[u]`` gives the color of node u.
        Pairs of adjacent nodes cannot be allocated to the same color. Any
        uncolored nodes ``u`` should have ``c[u]`` set to ``-1``.

    v : node
        The node the $s$-chain is to be generated from.

    L : list
        A sequence of unique colors, represented by integers. The first color
        in ``L`` should be the current color of ``v``.

    Returns
    -------
    set
        The set of nodes in the corresponding $s$-chain.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.node_coloring(G)
    >>> C = gcol.s_chain(G, c, 0, [0, 1, 2])
    >>> print("s-chain =", C)
    s-chain = {0, 1, 2, ..., 19}
    >>> C = gcol.s_chain(G, c, 0, [0, 2, 1])
    >>> print("s-chain =", C)
    s-chain = {0}

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

    ValueError
        If ``v`` is not present in ``G``.

        If ``G`` has a node that is not present in ``c``.

        If ``c`` contains a pair of adjacent nodes assigned to the same color.

        If ``L`` is not a list or tuple, has a length of less than two, or
        contains repeated values.

        If the first value of ``L`` is not equal to ``c[v]``

        If ``L`` contains values that are not in the set
        $\\{0,1,2,\\ldots\\}$.

    Notes
    -----
    This method uses a modified version of breadth-first search and operates in
    $O(m)$ time.

    See Also
    --------
    kempe_chain
    equitable_node_k_coloring

    References
    ----------
    .. [1] Morgenstern, C. and H. Shapiro (1990), Coloration Neighborhood
       Structures for General Graphs
       <https://dl.acm.org/doi/pdf/10.5555/320176.320202>

    """
    if G.is_directed() or G.is_multigraph() or nx.number_of_selfloops(G) > 0:
        raise NotImplementedError(
            "Error, this method cannot be used with directed graphs,",
            "multigraphs, or graphs with self-loops"
        )
    if v not in G:
        raise ValueError("Node v must be present in G")
    for u in G:
        for w in G[u]:
            if u not in c or w not in c:
                raise ValueError("All nodes in G must be present in c")
            if c[u] != -1 and c[w] != -1 and c[u] == c[w]:
                raise ValueError(
                    "This method does not permit adjacent nodes of the ",
                    "same color. Also, uncolored nodes u must have c[u] == -1"
                )
    if not isinstance(L, list) and not isinstance(L, tuple):
        raise ValueError("L parameter should be a list or tuple of colors")
    if len(L) <= 1 or len(L) != len(set(L)):
        raise ValueError("L must be nonempty. Repeated values are not allowed")
    if c[v] != L[0]:
        raise ValueError("Color of v must correspond to the first item in L")
    for j in L:
        if not isinstance(j, int) or j < 0:
            raise ValueError(
                "Colors labels in L must be integers in the set ",
                "{0, 1, 2, ...}"
            )
    # Checks completed. Calculate the s-chain using breadth-first search
    status = {v: 1}
    Q = deque([(v, 0)])
    Chain = set()
    while Q:
        u, pos = Q[0]
        nextpos = (pos + 1) % len(L)
        j = L[nextpos]
        for w in G[u]:
            if c[w] == j:
                if w not in status:
                    status[w] = 1
                    Q.append((w, nextpos))
        Q.popleft()
        status[u] = 2
        Chain.add(u)
    return Chain


def kempe_chain(G, c, v, i, j):
    """Return the set of nodes in a Kempe chain.

    Given a proper node coloring of graph $G$, a Kempe chain is a
    connected component in the graph induced by nodes of color $i$ and
    $j$. This method returns the Kempe chain containing the
    prescribed node $v$, where the color of $v$ is $i$. Any uncolored
    nodes (i.e., those whose colors are set to ``-1``) are ignored [1]_.

    The colors $i$ and $j$ alternate along any path in a Kempe chain. In a
    proper coloring, interchanging the colors of all nodes in a Kempe
    chain creates a new proper coloring. Two $k$-colorings of a graph are
    considered *Kempe equivalent* if one can be obtained from the other through
    a series of Kempe chain interchanges. It is known that, if $k$ is
    larger than the degeneracy of the graph $G$, then all $k$-colorings of $G$
    are Kempe equivalent [2]_.

    Parameters
    ----------
    G : NetworkX graph
        The graph that we want to compute a Kempe chain for.

    c : dict
        A node coloring of ``G``. Pairs of adjacent nodes cannot be allocated
        to the same color. Any uncolored nodes ``u`` should have ``c[u]`` set
        to ``-1``.

    v : node
        The node the Kempe chain is generated from.

    i : int
        The first color to use. This is the current color of ``v``.

    j : int
        The second color to use. Must be different to ``i``.

    Returns
    -------
    set
        The set of nodes in the corresponding Kempe chain.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.node_coloring(G)
    >>> C = gcol.kempe_chain(G, c, 0, 0, 1)
    >>> print("Kempe chain =", C)
    Kempe chain = {0, 1, 2, 4, 6, 8, 10, 17, 18, 19}

    Raises
    ------
    ValueError
        If ``i`` and ``j`` are equal.

        If ``v`` is not assigned to color ``i`` in ``c``.

        If ``v`` is not present in ``G``.

    Notes
    -----
    A Kempe chain is simply an $s$-chain using $s=2$ colors. As such, this
    method applies the :meth:`s_chain` method.

    See Also
    --------
    s_chain
    equitable_node_k_coloring

    References
    ----------
    .. [1] Wikipedia: Kempe Chain
      <https://en.wikipedia.org/wiki/Kempe_chain>
    .. [2] Cranston, D. (2024) Graph Coloring Methods
      <https://graphcoloringmethods.com/>

    """
    if i == j:
        raise ValueError("Colors i and j should be different")
    if v not in G:
        raise ValueError("Node v must be present in G")
    if c[v] != i:
        raise ValueError("Color of v must be equal to i")
    return s_chain(G, c, v, (i, j))


def max_independent_set(G, weight=None, it_limit=0, verbose=0):
    """Attempt to identify the largest independent set of nodes in a graph.

    Here, nodes can also be allocated weights if desired.

    The maximum independent set in a graph $G$ is the largest subset of nodes
    in which none are adjacent. The size of the largest independent in a graph
    $G$ is known as the independence number of $G$ and is often denoted by
    $\\alpha(G)$. Similarly, the maximum-weighted independent set in $G$ is
    the subset of mutually nonadjacent nodes whose weight-total is maximized.

    The problem of determining a maximum(-weighted) independent set of nodes
    is NP-hard. Consequently, this method makes use of a polynomial-time
    heuristic based on local search. It will always return an independent
    set but offers no guarantees on whether this is the optimal solution. The
    algorithm halts once the iteration limit has been reached.

    Note that the similar problem of determining the maximum(-weighted)
    independent set of edges is equivalent to finding a maximum(-weighted)
    matching in a graph. This is a polynomially solvable problem and can be
    solved by the Blossom algorithm.

    Parameters
    ----------
    G : NetworkX graph
        An independent set of nodes in this graph will be returned.

    weight : None or string, optional (default=None)
        If ``None``, every node is assumed to have a weight of ``1``. If a
        string, this should correspond to a defined node attribute. All node
        weights must be positive.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Each iteration has
        a complexity $O(m + n)$, where $n$ is the number of nodes and $m$ is
        the number of edges.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process. In this output, the cost refers to the number
        of nodes not in the independent set.

    Returns
    -------
    list
        A list containing the nodes belonging to the independent set.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> S = gcol.max_independent_set(G, it_limit=1000)
    >>> print("Independent set =", S)
    Independent set = [19, 10, 2, 8, 5, 12, 14, 17]
    >>>
    >>> # Do similar with a node-weighted graph
    >>> G = nx.Graph()
    >>> G.add_node(0, weight=20)
    >>> G.add_node(1, weight=9)
    >>> G.add_node(2, weight=25)
    >>> G.add_node(3, weight=10)
    >>> G.add_edges_from([(0,2), (1,2), (3, 2)])
    >>> S = gcol.max_independent_set(G, weight="weight", it_limit=1000)
    >>> print("Independent set =", S)
    Independent set = [0, 1, 3]

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

    ValueError
        If ``it_limit`` is not a nonnegative integer.

        If ``verbose`` is not a nonnegative integer.

        If a node with a non-positive weight is specified.

    KeyError
        If a node does not have the attribute defined by ``weight``.

    Notes
    -----
    This method uses the PartialCol algorithm for node $k$-coloring using
    $k=1$. The set of nodes assigned to this color corresponds to the
    independent set. PartialCol is based on tabu search. Here, each iteration
    of PartialCol has complexity $O(n + m)$. It also occupies $O(n + m)$ of
    memory space.

    The above algorithm is described in detail in [1]_. The c++ code used in
    [1]_ and [2]_ forms the basis of this library's Python implementations.

    See Also
    --------
    node_k_coloring
    node_coloring

    References
    ----------
    .. [1] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
      Applications (second ed.). Springer. ISBN: 978-3-030-81053-5.
      <https://link.springer.com/book/10.1007/978-3-030-81054-2>.
    .. [2] Lewis, R: Graph Colouring Algorithm User Guide
      <https://rhydlewis.eu/gcol/>

    """
    _check_params(G, "dsatur", 3, it_limit, verbose)
    if len(G) == 0:
        return {}
    elif G.number_of_edges() == 0:
        return list(G)
    W = _getNodeWeights(G, weight)
    # Make an initial coloring via dsatur and uncolor all but the first color
    # class
    c = _dsatur(G)
    for v in c:
        if c[v] > 0:
            c[v] = -1
    cost, c, its = _partialcol(G, 1, c, W, it_limit, verbose)
    return [v for v in c if c[v] == 0]


def min_cost_k_coloring(G, k, weight=None, weights_at="nodes", it_limit=0,
                        HEA=False, verbose=0):
    """Color the nodes of the graph using ``k`` colors.

    This is done so that a cost function is minimized. Equivalently, this
    routine partitions a graph's nodes while attempting to minimize a specific
    cost function.

    This routine will always produce a $k$-coloring. However, this solution
    may include some clashes (that is, instances of adjacent nodes having the
    same color), or uncolored nodes. The aim is to minimize the number (or
    total weight) of these occurrences.

    Determining a minimum cost solution to these problems is NP-hard. This
    routine employs polynomial-time heuristic algorithms based on local search.

    Parameters
    ----------
    G : NetworkX graph
        The nodes of this graph will be colored.

    k : int
        The number of colors to use.

    weight : None or string, optional (default=None)
        If ``None``, every node and edge is assumed to have a weight of ``1``.
        If string, this should correspond to a defined node or edge attribute.
        All node and edge weights must be positive.

    weights_at : string, optional (default='nodes')
        A string that must be one of the following:

        * ``'nodes'`` : Here, nodes can be left uncolored in a solution. If
          ``weight=None``, the method seeks a $k$-coloring in which the number
          of uncolored nodes is minimized; otherwise, the method seeks a
          $k$-coloring that minimizes the sum of the weights of the uncolored
          nodes. Clashes are not permitted in a solution. The algorithm halts
          when a zero-cost solution has been determined (this corresponds to a
          full, proper node $k$-coloring), or when the iteration limit is
          reached.
        * ``'edges'`` : Here, clashes are permitted in a solution. If
          ``weight=None``, the method seeks a $k$-coloring in which the number
          of clashes is minimized; otherwise, the method seeks a coloring that
          minimizes the sum of the weights of edges involved in a clash.
          Uncolored nodes are not permitted in a solution. The algorithm halts
          when a zero-cost solution has been determined (this corresponds to a
          full, proper node $k$-coloring), or when the iteration limit is
          reached.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Each iteration has
        a complexity $O(m + kn)$, where $n$ is the number of nodes, $m$ is the
        number of edges, and $k$ is the number of colors.

    HEA : bool, optional (default=False)
        If set to ``True``, a hybrid evolutionary algorithm is used in
        conjunction with local search; otherwise, only local search is used.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process.

    Returns
    -------
    dict
        A dictionary with keys representing nodes and values representing
        their colors. Colors are identified by the integers
        $0,1,2,\\ldots,k-1$. Uncolored nodes are given a value of ``-1``.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> # Unweighted graph
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.min_cost_k_coloring(G, 2, weights_at="nodes", it_limit=1000)
    >>> P = gcol.partition(c)
    >>> print(P)
    [[0, 2, 8, 18, 4, 13, 15], [1, 19, 10, 6, 12, 14, 17]]
    >>> for u in G:
    >>>     if c[u] == -1:
    >>>         print("Node", u, "is not colored")
    Node 3 is not colored
    Node 5 is not colored
    Node 7 is not colored
    Node 9 is not colored
    Node 11 is not colored
    Node 16 is not colored
    >>>
    >>> # Edge-weighted graph (arbitrary weights)
    >>> for e in G.edges():
    >>>     G.add_edge(e[0], e[1], weight = abs(e[0]-e[1]))
    >>> c = gcol.min_cost_k_coloring(G, 2, weights_at="edges", it_limit=1000)
    >>> P = gcol.partition(c)
    >>> print(P)
    [[0, 2, 8, 18, 11, 7, 4, 13, 15, 16], [1, 19, 10, 3, 9, 6, 5, 12, 14, 17]]
    >>> for u, v in G.edges():
    >>>     if c[u] == c[v]:
    >>>         print("Edge", u, v, "( cost =", G[u][v]["weight"], ") clashes")
    Edge 3 19 ( cost = 16 ) clashes
    Edge 5 6 ( cost = 1 ) clashes
    Edge 7 8 ( cost = 1 ) clashes
    Edge 9 10 ( cost = 1 ) clashes
    Edge 11 18 ( cost = 7 ) clashes
    Edge 15 16 ( cost = 1 ) clashes

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

    ValueError
        If ``weights_at`` is not among the supported options.

        If ``it_limit`` is not a nonnegative integer.

        If ``verbose`` is not a nonnegative integer.

        If ``k`` is not a nonnegative integer.

        If a node/edge with a non-positive weight is specified.

    KeyError
        If ``weights_at=='nodes'`` and a node does not have the attribute
        defined by ``weight``.

        If ``weights_at=='edges'`` and an edge does not have the attribute
        defined by ``weight``.

    Notes
    -----
    If ``weights_at='edges'``, the TabuCol algorithm is used. This algorithm
    is based on tabu search and operates using $k$ colors, allowing clashes
    to occur. The aim is to alter the color assignments so that the number
    of clashes (or the total weight of all clashing edges) is minimized. Each
    iteration of TabuCol has complexity $O(nk + m)$. The process also uses
    $O(nk + m)$ memory.

    If ``weights_at='nodes'``, the PartialCol algorithm is used. This algorithm
    is also based on tabu search and operates using $k$ colors, allowing some
    nodes to be left uncolored. The aim is to make alterations to the color
    assignments so that the number of uncolored nodes (or the total weight of
    the uncolored nodes) is minimized. As with TabuCol, each iteration of
    PartialCol has complexity $O(nk +m)$. This process also uses $O(nk + m)$
    memory.

    Further details on the local search and hybrid evolutionary algorithms, can
    be found in the notes section of the :meth:`node_coloring` method.

    All the above algorithms are described in detail in [1]_. The c++ code
    used in [1]_ and [2]_ forms the basis of this library's Python
    implementations.

    See Also
    --------
    node_k_coloring

    References
    ----------
    .. [1] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
      Applications (second ed.). Springer. ISBN: 978-3-030-81053-5.
      <https://link.springer.com/book/10.1007/978-3-030-81054-2>.
    .. [2] Lewis, R: Graph Colouring Algorithm User Guide
      <https://rhydlewis.eu/gcol/>

    """
    if k < 0:
        raise ValueError("Error, nonnegative integer needed for k")
    if weights_at not in {"nodes", "edges"}:
        raise ValueError(
            "Error, weights_at should be either 'nodes' or 'edges'"
        )
    _check_params(G, "dsatur", 3, it_limit, verbose)
    if len(G) == 0:
        return {}
    c = _dsatur(G)
    if weights_at == "nodes":
        W = _getNodeWeights(G, weight)
        for v in c:
            if c[v] >= k:
                c[v] = -1
        if HEA is True:
            cost, c, its = _HEA(G, k, c, W, it_limit, verbose, False)
        else:
            cost, c, its = _partialcol(G, k, c, W, it_limit, verbose)
    else:
        W = _getEdgeWeights(G, weight)
        for v in c:
            if c[v] >= k:
                c[v] = random.randint(0, k - 1)
        if HEA is True:
            cost, c, its = _HEA(G, k, c, W, it_limit, verbose, True)
        else:
            cost, c, its = _tabucol(G, k, c, W, it_limit, verbose)
    return c


def equitable_node_k_coloring(G, k, weight=None, opt_alg=None, it_limit=0,
                              verbose=0):
    """Attempt to color the nodes of a graph using ``k`` colors.

    This is done so that (a) all adjacent nodes have different colors, and (b)
    the weight of each color class is equal. If ``weight=None``, the weight of
    a color class is the number of nodes assigned to that color; otherwise,
    it is the sum of the weights of the nodes assigned to that color.

    Equivalently, this routine seeks to partition the graph's nodes into ``k``
    independent sets so that the weight of each independent set is equal.

    Determining an equitable node $k$-coloring is NP-hard. This method first
    follows the steps used by the :meth:`node_k_coloring` method to try and
    find a node $k$-coloring. If this is achieved, the algorithm then uses a
    bespoke local search operator to reduce the standard deviation in weights
    across the $k$ colors.

    If a node $k$-coloring cannot be determined by the algorithm, a
    ``ValueError`` exception is raised. Otherwise, a node $k$-coloring is
    returned in which the standard deviation in weights across the $k$ color
    classes has been minimized. In solutions returned by this method,
    neighboring nodes always receive different colors; however, the coloring
    is not guaranteed to be equitable, even if an equitable node $k$-coloring
    exists.

    Parameters
    ----------
    G : NetworkX graph
        The nodes of this graph will be colored.

    k : int
        The number of colors to use.

    weight : None or string, optional (default=None)
        If ``None``, every node is assumed to have a weight of ``1``. If
        string, this should correspond to a defined node attribute. Node
        weights must be positive.

    opt_alg : int, optional (default=None)
        An integer specifying the optimization method that will be used to try
        to reduce the number of colors (if this is seen to be greater than
        $k$). It must be one of the following

        * ``1`` : An exact, exponential-time algorithm based on backtracking.
          The algorithm halts only when the existence of a node $k$-coloring
          has been proved or disproved.
        * ``2`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing adjacent nodes to have the same color.
          Each iteration has a complexity $O(m + kn)$, where $n$ is the number
          of nodes in the modified graph, $m$ is the number of edges, and $k$
          is the number of colors in the current solution.
        * ``3`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes to be uncolored. Each iteration
          has a complexity $O(m + kn)$, as above.
        * ``4`` : A hybrid evolutionary algorithm (HEA) that evolves a small
          population of solutions. During execution, when each new solution is
          created, the local search method used in Option ``2`` above is
          applied for a fixed number of iterations. Each iteration of this HEA
          therefore has a complexity of $O(m + kn)$, as above.
        * ``5`` : A hybrid evolutionary algorithm is applied (as above), using
          the local search method from Option ``3``.
        * ``None`` : No optimization is performed.

        Further details of these algorithms are given in the notes section of
        the :meth:`node_coloring` method.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Not applicable
        when using ``opt_alg=1``.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process. The higher the value, the more information.

    Returns
    -------
    dict
        A dictionary with keys representing nodes and values representing their
        colors. Colors are identified by the integers $0,1,2,\\ldots,k-1$.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.equitable_node_k_coloring(G, 4)
    >>> P = gcol.partition(c)
    >>> print(P)
    [[0, 2, 9, 5, 14], [1, 3, 11, 7, 17], ..., [10, 18, 4, 12, 15]]
    >>> print("Size of smallest color class =", min(len(j) for j in P))
    Size of smallest color class = 5
    >>> print("Size of biggest color class =", max(len(j) for j in P))
    Size of biggest color class = 5
    >>>
    >>> #Now do similar with a node-weighted graph
    >>> G = nx.Graph()
    >>> G.add_node(0, weight=20)
    >>> G.add_node(1, weight=9)
    >>> G.add_node(2, weight=25)
    >>> G.add_node(3, weight=10)
    >>> G.add_edges_from([(0,2), (1,2), (3, 2)])
    >>> c = gcol.equitable_node_k_coloring(G, 3, weight="weight")
    >>> P = gcol.partition(c)
    >>> print(P)
    [[2], [0], [1, 3]]
    >>>
    >>> print(
    ...     "Weight of lightest color class =",
    ...     min(sum(G.nodes[v]['weight'] for v in j) for j in P)
    ... )
    Weight of lightest color class = 19
    >>>
    >>> print(
    ...     "Weight of heaviest color class =",
    ...     max(sum(G.nodes[v]['weight'] for v in j) for j in P)
    ... )
    Weight of heaviest color class = 25

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

    ValueError
        If ``opt_alg`` is not among the supported options.

        If ``it_limit`` is not a nonnegative integer.

        If ``verbose`` is not a nonnegative integer.

        If ``k`` is not a nonnegative integer.

        If a clique larger than ``k`` is observed in the graph.

        If a node $k$-coloring could not be determined.

        If a node with a non-positive weight is specified.

    KeyError
        If a node does not have the attribute defined by ``weight``

    Notes
    -----
    This method first follows the same steps as the :meth:`node_k_coloring`
    method to try and find a node $k$-coloring; however, it also takes node
    weights into account if needed. If a node $k$-coloring is achieved, a
    bespoke local search operator (based on steepest descent) is then used to
    try to reduce the standard deviation in weights across the $k$ color
    classes. This process involves evaluating each Kempe-chain interchange in
    the current solution [1]_ and performing the interchange that results in
    the largest reduction in standard deviation. This process repeats until
    there are no interchanges that reduce the standard deviation. Each
    iteration of this local search process takes $O(n^2)$ time. Further details
    on this optimization method can be found in Chapter 7 of [2], or in [3]_.

    All the above algorithms are described in detail in [2]_. The c++ code used
    in [2]_ and [4]_ forms the basis of this library's Python implementations.

    See Also
    --------
    node_k_coloring
    kempe_chain
    :meth:`gcol.edge_coloring.equitable_edge_k_coloring`

    References
    ----------
    .. [1] Wikipedia: Kempe Chain <https://en.wikipedia.org/wiki/Kempe_chain>
    .. [2] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
      Applications (second ed.). Springer. ISBN: 978-3-030-81053-5.
      <https://link.springer.com/book/10.1007/978-3-030-81054-2>.
    .. [3] Lewis, R. and F. Carroll (2016) 'Creating Seating Plans: A Practical
      Application'. Journal of the Operational Research Society, vol. 67(11),
      pp. 1353-1362.
    .. [4] Lewis, R: Graph Colouring Algorithm User Guide
      <https://rhydlewis.eu/gcol/>

    """
    if k < 0:
        raise ValueError("Error, nonnegative integer needed for k")
    _check_params(G, "dsatur", opt_alg, it_limit, verbose)
    if len(G) == 0:
        return {}
    cliqueNum = nx.approximation.large_clique_size(G)
    if k < cliqueNum:
        raise ValueError(
            "Error, a clique of size greater than k exists in the graph, so "
            "a k-coloring is not possible. Try increasing k"
        )
    W = _getNodeWeights(G, weight)
    c = _dsatur_equitable(G, k, W)
    if c is None:
        if opt_alg is None:
            raise ValueError(
                "Error, a k-coloring could not be found. Try changing the "
                "optimisation options or increasing k"
            )
        c = _dsatur(G)
        if opt_alg in [2, 4]:
            WPrime = _getEdgeWeights(G, None)
        else:
            WPrime = _getNodeWeights(G, None)
        c = _reducecolors(G, c, k, WPrime, opt_alg, it_limit, verbose)
        if max(c.values()) + 1 > k:
            raise ValueError(
                "Error, could not construct a k-coloring of this graph. Try "
                "increasing k or using more optimisation"
            )
    # If we are here we have a k-coloring. Attempt to decrease the SD
    # across the color classes using a steepest descent heuristic
    return _LS_equitable(G, c, k, W, verbose)


def node_k_coloring(G, k, opt_alg=None, it_limit=0, verbose=0):
    """Attempt to color the nodes of a graph using ``k`` colors.

    This is done so that adjacent nodes have different colors. A set of nodes
    assigned to the same color corresponds to an independent set; hence the
    equivalent aim is to partition the graph's nodes into ``k`` independent
    sets.

    Determining whether a node $k$-coloring exists for $G$ is NP-complete.
    This method therefore includes options for using an exact exponential-time
    algorithm (based on backtracking), or a choice of four polynomial-time
    heuristic algorithms (based on local search). The exact algorithm is
    generally only suitable for larger values of $k$, for graphs that are
    small, or graphs that have topologies suited to its search strategies. In
    all other cases, the local search algorithms are more appropriate.

    If a node $k$-coloring cannot be determined by the algorithm, a
    ``ValueError`` exception is raised. Otherwise, a node $k$-coloring is
    returned.

    Parameters
    ----------
    G : NetworkX graph
        The nodes of this graph will be colored.

    k : int
        The number of colors to use.

    opt_alg : None or int, optional (default=None)
        An integer specifying the optimization method that will be used to try
        to reduce the number of colors (if this is seen to be greater than
        $k$). It must be one of the following

        * ``1`` : An exact, exponential-time algorithm based on backtracking.
          The algorithm halts only when the existence of a node $k$-coloring
          has been proved or disproved.
        * ``2`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing adjacent nodes to have the same color.
          Each iteration has a complexity $O(m + kn)$, where $n$ is the number
          of nodes in the graph, $m$ is the number of edges, and $k$ is the
          number of colors in the current solution.
        * ``3`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes to be uncolored. Each iteration
          has a complexity $O(m + kn)$, as above.
        * ``4`` : A hybrid evolutionary algorithm (HEA) that evolves a small
          population of solutions. During execution, when each new solution is
          created, the local search method used in Option ``2`` above is
          applied for a fixed number of iterations. Each iteration of this HEA
          therefore has a complexity of $O(m + kn)$, as above.
        * ``5`` : A hybrid evolutionary algorithm is applied (as above), using
          the local search method from Option ``3``.
        * ``None`` : No optimization is performed.

        Further details of these algorithms are given in the notes section of
        the :meth:`node_coloring` method.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Not applicable
        when using ``opt_alg=1``.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process. The higher the value, the more information.

    Returns
    -------
    dict
        A dictionary with keys representing edges and values representing their
        colors. Colors are identified by the integers $0,1,2,\\ldots,k-1$.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.node_k_coloring(G, 4)
    >>> print(c)
    {0: 0, 1: 1, 19: 2, 10: 3, 2: 0, ..., 15: 3}
    >>>
    >>> c = gcol.node_k_coloring(G, 3)
    >>> print(c)
    {0: 0, 1: 1, 19: 2, 10: 1, 2: 0, ..., 12: 1}

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

    ValueError
        If ``opt_alg`` is not among the supported options.

        If ``it_limit`` is not a nonnegative integer.

        If ``verbose`` is not a nonnegative integer.

        If ``k`` is not a nonnegative integer.

        If a clique larger than ``k`` is observed in the graph.

        If a node $k$-coloring could not be determined.

    Notes
    -----
    This method begins by coloring the nodes in the order determined by the
    DSatur algorithm [1]_. During this process, each node is assigned to the
    feasible color class $j$ (where $0 \\leq j \\leq k$) with the fewest nodes.
    This encourages an equitable spread of nodes across the $k$ colors. This
    process has a complexity of $O((n \\lg n) + (nk) + (m \\lg m)$. If a node
    $k$-coloring cannot be achieved in this way, further optimization is
    carried out, if desired. These optimization routines are the same as those
    used by the :meth:`node_coloring` method. They also halt immediately once
    a node $k$-coloring has been achieved.

    All the above algorithms are described in detail in [2]_. The c++ code used
    in [2]_ and [3]_ forms the basis of this library's Python implementations.

    See Also
    --------
    node_coloring
    equitable_node_k_coloring
    :meth:`gcol.edge_coloring.edge_k_coloring`

    References
    ----------
    .. [1] Wikipedia: DSatur <https://en.wikipedia.org/wiki/DSatur>
    .. [2] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
      Applications (second ed.). Springer. ISBN: 978-3-030-81053-5.
      <https://link.springer.com/book/10.1007/978-3-030-81054-2>.
    .. [3] Lewis, R: Graph Colouring Algorithm User Guide
      <https://rhydlewis.eu/gcol/>

    """
    if k < 0:
        raise ValueError("Error, nonnegative integer needed for k")
    _check_params(G, "dsatur", opt_alg, it_limit, verbose)
    if len(G) == 0:
        return {}
    cliqueNum = nx.approximation.large_clique_size(G)
    if k < cliqueNum:
        raise ValueError(
            "Error, a clique of size greater than k exists in the graph, so "
            "a k-coloring is not possible. Try increasing k"
        )
    W = _getNodeWeights(G, None)
    c = _dsatur_equitable(G, k, W)
    if c is None:
        if opt_alg is None:
            raise ValueError(
                "Error, a k-coloring could not be found. Try changing the "
                "optimisation options or increasing k"
            )
        c = _dsatur(G)
        if opt_alg in [2, 4]:
            W = _getEdgeWeights(G, None)
        c = _reducecolors(G, c, k, W, opt_alg, it_limit, verbose)
        if max(c.values()) + 1 > k:
            raise ValueError(
                "Error, could not construct a k-coloring of this graph. Try "
                "increasing k or using more optimisation"
            )
    # If we are here we have a k-coloring
    return c


def node_coloring(G, strategy="dsatur", opt_alg=None, it_limit=0, verbose=0):
    """Return a coloring of a graph's nodes.

    A node coloring of a graph is an assignment of colors to nodes so that
    adjacent nodes have different colors. The aim is to use as few colors as
    possible. A set of nodes assigned to the same color represents an
    independent set; hence the equivalent aim is to partition the graph's nodes
    into a minimum number of independent sets.

    The smallest number of colors needed to color the nodes of a graph $G$ is
    known as the graph's chromatic number, denoted by $\\chi(G)$. Equivalently,
    $\\chi(G)$ is the minimum number of independent sets needed to partition
    the nodes of $G$.

    Determining a node coloring that minimizes the number of colors is an
    NP-hard problem. This method therefore includes options for using an exact
    exponential-time algorithm (based on backtracking), or a choice of four
    polynomial-time heuristic algorithms (based on local search). The exact
    algorithm is generally only suitable for graphs that are small, or that
    have topologies suited to its search strategies. In all other cases, the
    local search algorithms are more appropriate.

    Parameters
    ----------
    G : NetworkX graph
        The nodes of this graph will be colored.

    strategy : string, optional (default='dsatur')
        A string specifying the method used to generate an initial solution. It
        must be one of the following:

        * ``'random'`` : Randomly orders the graph's nodes and then applies the
          greedy algorithm for graph node coloring [1]_.
        * ``'welsh-powell'`` : Orders the graph's nodes by decreasing degree,
          then applies the greedy algorithm.
        * ``'dsatur'`` : Uses the DSatur algorithm for graph node coloring
          [2]_.
        * ``'rlf'`` : Uses the recursive largest first (RLF) algorithm for
          graph node coloring [3]_.

    opt_alg : None or int, optional (default=None)
        An integer specifying the optimization method that will be used to try
        to reduce the number of colors. It must be one of the following

        * ``1`` : An exact, exponential-time algorithm based on backtracking.
          The algorithm halts only when an optimal solution has been found.
        * ``2`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing adjacent nodes to have the same color.
          Each iteration has a complexity $O(m + kn)$, where $n$ is the number
          of nodes in the graph, $m$ is the number of edges, and $k$ is the
          number of colors in the current solution.
        * ``3`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes to be uncolored. Each iteration
          has a complexity $O(m + kn)$, as above.
        * ``4`` : A hybrid evolutionary algorithm (HEA) that evolves a small
          population of solutions. During execution, when each new solution is
          created, the local search method used in Option ``2`` above is
          applied for a fixed number of iterations. Each iteration of this HEA
          therefore has a complexity of $O(m + kn)$, as above.
        * ``5`` : A hybrid evolutionary algorithm is applied (as above), using
          the local search method from Option ``3``.
        * ``None`` : No optimization is performed.

        Further details of these algorithms are given below.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Not applicable
        when using ``opt_alg=1``.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process. The higher the value, the more information.

    Returns
    -------
    dict
        A dictionary with keys representing nodes and values representing their
        colors. Colors are identified by the integers $0,1,2,\\ldots$. The
        number of colors being used in a solution ``c`` is therefore
        ``max(c.values()) + 1``.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.node_coloring(G)
    >>> print("Coloring is", c)
    Coloring is {0: 0, 1: 1, 19: 1, 10: 1, 2: 0, ..., 17: 1}
    >>> print("Number of colors =", max(c.values()) + 1)
    Number of colors = 3
    >>>
    >>> print("Partition view =", gcol.partition(c))
    Partition view = [[0, 2, 8, 18, 4, 13, 15], ..., [3, 9, 11, 7, 5, 16]]
    >>>
    >>> # Example with a larger graph and different parameters
    >>> G = nx.gnp_random_graph(50, 0.2, seed=1)
    >>> c = gcol.node_coloring(G, strategy="dsatur", opt_alg=2, it_limit=1000)
    >>> print("Coloring is", c)
    Coloring is {18: 0, 31: 2, 2: 4, 20: 1, 10: 3, ..., 27: 2}
    >>>
    >>> print("Number of colors =", max(c.values()) + 1)
    Number of colors = 5

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

    ValueError
        If ``strategy`` is not among the supported options.

        If ``opt_alg`` is not among the supported options.

        If ``it_limit`` is not a nonnegative integer.

        If ``verbose`` is not a nonnegative integer.

    Notes
    -----
    Given a graph $G=(V,E)$ with $n$ nodes and $m$ edges, the greedy algorithm
    for node coloring operates in $O(n + m)$ time.

    The ``random`` strategy operates by first randomly permuting the nodes (an
    $O(n)$ operation) before applying the greedy algorithm. It is guaranteed to
    produce a solution with $k \\leq \\Delta(G) + 1$ colors, where
    $\\Delta(G)$ is the highest node degree in the graph $G$.

    The ``welsh-powell`` strategy operates by sorting the nodes by decreasing
    degree (an $O(n \\lg n)$ operation), and then applies the greedy algorithm.
    Its overall complexity is therefore $O(n \\lg n + m)$. Assuming that the
    nodes are labelled $v_1, v_2,\\ldots,v_n$ so that $\\deg(v_1) \\geq
    \\deg(v_2) \\geq \\ldots \\geq \\deg(v_n)$, this method is guaranteed to
    produce a solution with $k \\leq\\max_{i=1,\\ldots,n} \\min(\\deg(v_i)+1,
    i)$ colors. This bound is an improvement on $\\Delta(G) + 1$.

    The ``dsatur`` and ``rlf`` strategies are exact for bipartite, cycle, and
    wheel graphs (that is, solutions with the minimum number of colors are
    guaranteed). The implementation of ``dsatur`` uses a priority queue and has
    a complexity of $O(n \\lg n + m \\lg m)$. The ``rlf`` implementation has a
    complexity of $O(nm)$. In general, the ``rlf`` strategy yields the best
    solutions of the four strategies, though it is computationally more
    expensive. If expense is an issue, then ``dsatur`` is a cheaper alternative
    that also offers high-quality solutions in most cases. See [2]_, [3]_, and
    [4]_ for further information.

    If an optimization algorithm is used, further efforts are made to reduce
    the number of colors. The backtracking approach (``opt_alg=1``) is an
    implementation of the exact algorithm described in [4]_. It has exponential
    runtime and halts only when an optimum solution has been found. At the
    start of execution, a large clique $C\\subseteq V$ is identified using the
    NetworkX function ``max_clique(G)`` and the nodes of $C$ are each assigned
    to a different color. The main backtracking algorithm is then executed and
    only halts only when a solution using $|C|$ colors has been identified, or
    when the algorithm has backtracked to the root of the search tree. In both
    cases the returned solution will be optimal (that is, will be using
    $\\chi(G)$ colors).

    If local search is used (``opt_alg`` is set to ``2``, ``3``, ``4``, or
    ``5``), the algorithm removes a color class and uses the chosen local
    search routine to seek a proper coloring using the remaining colors. This
    process repeats until a solution using $|C|$ colors has been identified
    (as above), or until the iteration limit (defined by ``it_limit``) is
    reached. Fewer colors (but longer run times) occur with larger iteration
    limits.

    If ``opt_alg=2``, the TabuCol algorithm is used. This algorithm is based
    on tabu search and operates by fixing the number of colors but allowing
    clashes to occur (a clash is the occurrence of two adjacent nodes having
    the same color). The aim is to alter the color assignments so that the
    number of clashes is reduced to zero. Each iteration of TabuCol has a
    complexity of $O(nk + m)$, where $k$ is the number of colors currently
    being used. The process also uses $O(nk + m)$ memory.

    If ``opt_alg=3``, the PartialCol algorithm is used. This algorithm is also
    based on tabu search and operates by fixing the number of colors but
    allowing some nodes to be left uncolored. The aim is to make alterations
    to the color assignments so that no uncolored nodes remain. As with
    TabuCol, each iteration of PartialCol has complexity $O(nk +m)$ and uses
    $O(nk + m)$ memory.

    If ``opt_alg`` is set to ``4`` or ``5``, a hybrid evolutionary algorithm
    (HEA) is used [5]_. This method maintains a small population of $k$-colored
    solutions that is evolved using selection, recombination, local search and
    replacement. Specifically, in each HEA cycle, two parent solutions are
    selected from the population, and these are used in conjunction with a
    specialised recombination operator to produce a new offspring solution.
    Local search is this applied to the offspring for a fixed number of
    iterations, and the resultant solution is inserted back into the
    population, replacing its weaker parent. If ``opt_alg=4``, TabuCol is
    used as the local search operator; if ``opt_alg=5``, PartialCol is used.
    Each iteration of the HEA has complexity $O(nk+m)$, as above. Note that
    the HEA is often able to produce solutions using fewer colors compared to
    when using ``opt_alg=2`` or ``opt_alg=3``; however, larger iteration
    limits will usually be needed to see these improvements.

    As stated above, if ``verbose`` is set to a positive integer, output is
    produced during the execution of the chosen optimzation algorithm. If the
    backtracking algorithm is being used, the stated iterations refer to the
    number of calls to its recursive function. Otherwise, iterations refer to
    the $O(nk +m)$ processes mentioned above. If no optimization is performed,
    no output is produced.

    All the above algorithms and bounds are described in detail in [4]_. The
    c++ code used in [4]_ and [6]_ forms the basis of this library's Python
    implementations.

    See Also
    --------
    chromatic_number
    node_k_coloring
    :meth:`gcol.edge_coloring.edge_coloring`

    References
    ----------
    .. [1] Wikipedia: Greedy Coloring
      <https://en.wikipedia.org/wiki/Greedy_coloring>
    .. [2] Wikipedia: DSatur <https://en.wikipedia.org/wiki/DSatur>
    .. [3] Wikipedia: Recursive largest first (RLF) algorithm
      <https://en.wikipedia.org/wiki/Recursive_largest_first_algorithm>
    .. [4] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
      Applications (second ed.). Springer. ISBN: 978-3-030-81053-5.
      <https://link.springer.com/book/10.1007/978-3-030-81054-2>.
    .. [5] Galinier, P. and J. Hao (1999). Hybrid Evolutionary Algorithms for
      Graph Coloring. Journal of Combinatorial Optimization 3, 379–397.
    .. [6] Lewis, R: Graph Colouring Algorithm User Guide
      <https://rhydlewis.eu/gcol/>

    """
    _check_params(G, strategy, opt_alg, it_limit, verbose)
    if len(G) == 0:
        return {}
    elif G.number_of_edges() == 0:
        return {u: 0 for u in G}
    # Make an initial coloring based on the chosen strategy
    if strategy == "random":
        V = list(G)
        random.shuffle(V)
        c = _greedy(G, V)
    elif strategy == "welsh_powell":
        V = sorted(G, key=G.degree, reverse=True)
        c = _greedy(G, V)
    elif strategy == "rlf":
        c = _rlf(G)
    else:
        c = _dsatur(G)
    # If selected, employ the chosen optimisation method
    if opt_alg is None:
        return c
    if opt_alg in [2, 4]:
        W = _getEdgeWeights(G, None)
    else:
        W = _getNodeWeights(G, None)
    cliqueNum = nx.approximation.large_clique_size(G)
    return _reducecolors(G, c, cliqueNum, W, opt_alg, it_limit, verbose)


def chromatic_number(G):
    """Return the chromatic number of the graph ``G``.

    The chromatic number of a graph $G$ is the minimum number of colors needed
    to color the nodes so that no two adjacent nodes have the same color. It is
    commonly denoted by $\\chi(G)$. Equivalently, $\\chi(G)$ is the minimum
    number of independent sets needed to partition the nodes of $G$.

    Determining the chromatic number is NP-hard. The approach used here is
    based on the backtracking algorithm of [1]_. This is exact but operates
    in exponential time. It is therefore only suitable for graphs that are
    small, or that have topologies suited to its search strategies.

    Parameters
    ----------
    G : NetworkX graph
        The chromatic number for this graph will be calculated.

    Returns
    -------
    int
        A nonnegative integer that gives the chromatic number of ``G``.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> chi = gcol.chromatic_number(G)
    >>> print("Chromatic number is", chi)
    Chromatic number is 3

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

    Notes
    -----
    The backtracking approach used here is an implementation of the exact
    algorithm described in [1]_. It has exponential runtime and halts only when
    the chromatic number has been determined. Further details of this algorithm
    are given in the notes section of the :meth:`node_coloring` method.

    The above algorithm is described in detail in [1]_. The c++ code used in
    [1]_ and [2]_ forms the basis of this library's Python implementations.

    See Also
    --------
    node_coloring
    :meth:`gcol.edge_coloring.chromatic_index`

    References
    ----------
    .. [1] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
      Applications (second ed.). Springer. ISBN: 978-3-030-81053-5.
      <https://link.springer.com/book/10.1007/978-3-030-81054-2>.
    .. [2] Lewis, R: Graph Colouring Algorithm User Guide
      <https://rhydlewis.eu/gcol/>

    """
    if G.is_directed() or G.is_multigraph() or nx.number_of_selfloops(G) > 0:
        raise NotImplementedError(
            "Error, this method cannot be used with directed graphs, "
            "multigraphs, or graphs containing self-loops."
        )
    if len(G) == 0:
        return 0
    cliqueNum = nx.approximation.large_clique_size(G)
    c = _backtrackcol(G, cliqueNum, 0)
    return max(c.values()) + 1


def node_precoloring(
    G, precol=None, strategy="dsatur", opt_alg=None, it_limit=0, verbose=0
):
    """Return a coloring of a graph's nodes where some nodes are precolored.

    A node coloring of a graph is an assignment of colors to nodes so that
    adjacent nodes have different colors. The aim is to use as few colors as
    possible. A set of nodes assigned to the same color corresponds to an
    independent set; hence the equivalent aim is to partition the graph's
    nodes into a minimum number of independent sets.

    In the node precoloring problem, some of the nodes have already been
    assigned colors. The aim is to allocate colors to the remaining nodes so
    that we get a full, proper node coloring that uses a minimum number of
    colors. The node precoloring problem can be used to model the Latin square
    completion problem and Sudoku puzzles [1]_.

    The node precoloring problem is NP-hard. This method therefore includes
    options for using an exponential-time exact algorithm (based on
    backtracking), or a choice of four polynomial-time heuristic algorithms
    (based on local search). The exact algorithm is generally only suitable
    for graphs that are small, or that have topologies suited to its search
    strategies. In all other cases, the local search algorithms are more
    appropriate.

    In this implementation, solutions are found by taking all nodes
    pre-allocated to the same color $j$ and merging them into a single
    super-node. Edges are then added between all pairs of super-nodes,
    and the modified graph is passed to the :meth:`node_coloring` method. All
    parameters are therefore the same as the latter. This modification process
    is described in more detail in Chapter 6 of [1]_.

    Parameters
    ----------
    G : NetworkX graph
        The nodes of this graph will be colored.

    precol : None or dict, optional (default=None)
        A dictionary that specifies the (integer) colors of any precolored
        nodes.

    strategy : string, optional (default='dsatur')
        A string specifying the method used to generate the initial solution.
        It must be one of the following:

        * ``'random'`` : Randomly orders the modified graph's nodes and then
          applies the greedy algorithm for graph node coloring [2]_.
        * ``'welsh-powell'`` : Orders the modified graphs nodes by decreasing
          degree, then applies the greedy algorithm.
        * ``'dsatur'`` : Uses the DSatur algorithm for graph node coloring on
          the modified graph [3]_.
        * ``'rlf'`` : Uses the recursive largest first (RLF) algorithm for
          graph node coloring on the modified graph [4]_.

    opt_alg : None or int, optional (default=None)
        An integer specifying the optimization method that will be used to
        try to reduce the number of colors. It must be one of the following

        * ``1`` : An exact, exponential-time algorithm based on backtracking.
          The algorithm halts only when an optimal solution has been found.
        * ``2`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing adjacent nodes to have the same color.
          Each iteration has a complexity $O(m + kn)$, where $n$ is the number
          of nodes in the modified graph, $m$ is the number of edges, and $k$
          is the number of colors in the current solution.
        * ``3`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes to be uncolored. Each iteration
          has a complexity $O(m + kn)$, as above.
        * ``4`` : A hybrid evolutionary algorithm (HEA) that evolves a small
          population of solutions. During execution, when each new solution is
          created, the local search method used in Option ``2`` above is
          applied for a fixed number of iterations. Each iteration of this HEA
          therefore has a complexity of $O(m + kn)$, as above.
        * ``5`` : A hybrid evolutionary algorithm is applied (as above), using
          the local search method from Option ``3``.
        * ``None`` : No optimization is performed.

        Further details of these algorithms are given in the notes section of
        the :meth:`node_coloring` method.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Not applicable
        when using ``opt_alg=1``.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process. The higher the value, the more information.

    Returns
    -------
    dict
        A dictionary with keys representing nodes and values representing their
        colors. Colors are identified by the integers $0,1,2,\\ldots$. The
        number of colors being used in a solution ``c`` is therefore
        ``max(c.values()) + 1``. If ``precol[v]==j`` then ``c[v]==j``.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> p = {0:1, 8:0, 9:1}
    >>> c = gcol.node_precoloring(G, precol=p)
    >>> print("Coloring is", c)
    Coloring is {0: 1, 9: 1, 1: 2, 8: 0, 19: 2, ..., 16: 0}
    >>>
    >>> p = {i:i for i in range(5)}
    >>> c = gcol.node_precoloring(
    ...     G, precol=p, strategy="dsatur", opt_alg=2, it_limit=1000
    ... )
    >>> print(c)
    {0: 0, 4: 4, 1: 1, 2: 2, 3: 3, ..., 12: 2}

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

    ValueError
        If ``strategy`` is not among the supported options.

        If ``opt_alg`` is not among the supported options.

        If ``it_limit`` is not a nonnegative integer.

        If ``verbose`` is not a nonnegative integer.

        If ``G`` contains a node with the name ``'super'``.

        If ``precol`` contains a node that is not in ``G``.

        If ``precol`` contains a non-integer color label.

        If ``precol`` contains a pair of adjacent nodes assigned the same
        color.

        If ``precol`` uses an integer color label $j$, but there exists a color
        label $0 \\leq i < j$ that is not being used.

    Notes
    -----
    As mentioned, in this implementation, solutions are formed by passing a
    modified version of the graph to :meth:`node_coloring` method. All details
    are therefore the same as those in the latter, where they are documented.

    All the above algorithms and bounds are described in detail in [1]. The c++
    code used in [1]_ and [5]_ forms the basis of this library's Python
    implementations.

    See Also
    --------
    node_coloring
    :meth:`gcol.edge_coloring.edge_precoloring`

    References
    ----------
    .. [1] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
      Applications (second ed.). Springer. ISBN: 978-3-030-81053-5.
      <https://link.springer.com/book/10.1007/978-3-030-81054-2>.
    .. [2] Wikipedia: Greedy Coloring
      <https://en.wikipedia.org/wiki/Greedy_coloring>
    .. [3] Wikipedia: DSatur <https://en.wikipedia.org/wiki/DSatur>
    .. [4] Wikipedia: Recursive largest first (RLF) algorithm
      <https://en.wikipedia.org/wiki/Recursive_largest_first_algorithm>
    .. [5] Lewis, R: Graph Colouring Algorithm User Guide
      <https://rhydlewis.eu/gcol/>

    """
    _check_params(G, strategy, opt_alg, it_limit, verbose)
    if len(G) == 0:
        return {}
    if precol is None or precol == {}:
        return node_coloring(
            G, strategy=strategy, opt_alg=opt_alg, it_limit=it_limit,
            verbose=verbose
        )
    if not isinstance(precol, dict):
        raise TypeError(
            "Error, the precoloring should be a dict"
        )
    for u in G:
        if isinstance(u, tuple) and u[0] == "super":
            raise ValueError(
                "Error, for this method, the name 'super' is reserved. "
                "Please use another name"
            )
    cols = set()
    for u in precol:
        if u not in G:
            raise ValueError(
                "Error, an entity is defined in the precoloring that's not in "
                "the graph"
            )
        if not isinstance(precol[u], int):
            raise ValueError(
                "Error, all color labels in the precoloring should be integers"
            )
        cols.add(precol[u])
        for v in G[u]:
            if v in precol and precol[u] == precol[v]:
                raise ValueError(
                    "Error, there are adjacent entities in the precoloring "
                    "with the same color"
                )
    k = max(precol.values()) + 1
    for i in range(k):
        if i not in cols:
            raise ValueError(
                "Error, the color labels in the precoloring should be in "
                "{0,1,2,...} and each color should be being used at least "
                "once"
            )
    # V[i] holds the set of nodes assigned to each color i
    V = defaultdict(set)
    for v in precol:
        V[precol[v]].add(v)
    # Form the graph GPrime. This incorporates the precolorings on G and
    # merges nodes of the same color into a single super-node
    GPrime = nx.Graph()
    for i in V:
        GPrime.add_node(("super", i))
    for v in G:
        if v not in precol:
            GPrime.add_node(v)
    for u in G:
        for v in G[u]:
            if u != v and u in GPrime and v in GPrime:
                GPrime.add_edge(u, v)
    for i in V:
        for u in V[i]:
            for v in G[u]:
                if v in GPrime:
                    GPrime.add_edge(("super", i), v)
    for i in V:
        for j in V:
            if i != j:
                GPrime.add_edge(("super", i), ("super", j))
    # Now color GPrime and use this solution to gain a coloring c for G
    cPrime = node_coloring(
        GPrime, strategy=strategy, opt_alg=opt_alg, it_limit=it_limit,
        verbose=verbose
    )
    k = max(cPrime.values()) + 1
    c = {}
    for u in cPrime:
        if isinstance(u, tuple) and u[0] == "super":
            for v in V[u[1]]:
                c[v] = cPrime[u]
        else:
            c[u] = cPrime[u]
    # Finally, apply a color relabeling to conform to the original precoloring
    colmap = {}
    for u in precol:
        colmap[c[u]] = precol[u]
    cnt = len(V)
    for i in range(k):
        if i not in colmap:
            colmap[i] = cnt
            cnt += 1
    for v in c:
        c[v] = colmap[c[v]]
    return c


# Alternative spellings of the above methods
equitable_node_k_colouring = equitable_node_k_coloring
min_cost_k_colouring = min_cost_k_coloring
node_colouring = node_coloring
node_k_colouring = node_k_coloring
node_precolouring = node_precoloring

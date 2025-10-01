"""Node coloring functions for the gcol library."""
import random
import itertools
import networkx as nx
from queue import PriorityQueue
from collections import defaultdict


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

    # Find a large clique C in G
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

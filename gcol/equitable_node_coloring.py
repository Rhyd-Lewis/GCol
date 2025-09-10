"""Equitable node coloring functions for the gcol library."""
from queue import PriorityQueue
from collections import deque
import itertools


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
    # class
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

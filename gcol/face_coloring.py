"""Method for converting planar embedding to a dual graph."""
import networkx as nx
import math


def _get_dual(G, pos):

    def getBearing(P, Q):
        P, Q = tuple(P), tuple(Q)
        # Get bearing of line PQ, where P and Q are both (x,y) coordinates.
        b = math.degrees(math.atan2(Q[1]-P[1], Q[0]-P[0]))
        return b + 360 if b < 0 else b

    def intersect(L1, L2):

        def getArea(x1, y1, x2, y2, x3, y3):
            return (x2-x1)*(y3-y1)-(x3-x1)*(y2-y1)

        x1, y1, x2, y2 = L1[0][0], L1[0][1], L1[1][0], L1[1][1]
        x3, y3, x4, y4 = L2[0][0], L2[0][1], L2[1][0], L2[1][1]
        epsilon = 0.000000001
        # The lines (x1y1)(x2y2) and (x3y3)(x4y4) are considered to intersect
        # iff they intersect and do not share exactly one endpoint. Epsilon
        # is used for rounding issues
        common_endpoints = {(x1, y1), (x2, y2)} & {(x3, y3), (x4, y4)}
        if len(common_endpoints) == 1:
            return False
        c_area = getArea(x1, y1, x2, y2, x3, y3)
        d_area = getArea(x1, y1, x2, y2, x4, y4)
        if abs(c_area) < epsilon:
            if abs(x3-x1) < epsilon:
                if min(y1, y2)-epsilon < y3 < max(y1, y2)+epsilon:
                    return True
            else:
                if min(x1, x2)-epsilon < x3 < max(x1, x2)+epsilon:
                    return True
            if abs(d_area) > epsilon:
                return False
        if abs(d_area) < epsilon:
            if abs(x4-x1) < epsilon:
                if min(y1, y2)-epsilon < y4 < max(y1, y2)+epsilon:
                    return True
            else:
                if min(x1, x2)-epsilon < x4 < max(x1, x2)+epsilon:
                    return True
            if abs(c_area) > epsilon:
                return False
            if abs(x3-x1) < epsilon:
                return (y1 < y3) != (y1 < y4)
            else:
                return (x1 < x3) != (x1 < x4)
        if (c_area > 0) == (d_area > 0):
            return False
        a_area = getArea(x3, y3, x4, y4, x1, y1)
        b_area = getArea(x3, y3, x4, y4, x2, y2)
        return (a_area > 0) != (b_area > 0)

    def embeddingIsPlanar(G, pos):
        # Return true iff none of the lines/edges in the embedding cross
        for u in G:
            if u not in pos:
                raise ValueError("Error, node in G that is not in pos")
        # Create a line for each edge in G, ensuring the left endpoint is first
        Lines = [(pos[u], pos[v]) if pos[u][0] <= pos[v][0] else
                 (pos[v], pos[u])
                 for u, v in G.edges()]
        # Make sorted list L of all endpoints. Each element is a tuple
        # indicating (x-coord, isRight, y-coord, index)
        L = []
        for i, ((x1, y1), (x2, y2)) in enumerate(Lines):
            L.append((x1, 0, y1, i))
            L.append((x2, 1, y2, i))
        L.sort()
        # Run a sweep algorithm using L.
        activeLines = set()
        for _, isRight, _, i in L:
            if isRight == 0:
                for j in activeLines:
                    if intersect(Lines[i], Lines[j]):
                        return False
                activeLines.add(i)
            else:
                activeLines.remove(i)
        return True

    def isClockwise(P):
        # Returns true iff the sequence of (x,y) coordinates in the list
        # P follows a clockwise direction
        area, n = 0, len(P)
        for i in range(n):
            x1, y1 = tuple(P[i])
            x2, y2 = tuple(P[(i + 1) % n])
            area += x1 * y2 - y1 * x2
        if area > 0:
            return False
        elif area < 0:
            return True
        else:
            raise ValueError("Invalid polygon P: " + str(P))

    # Check the supplied graph and postions dictionary give a planar,
    # bridge-free embedding
    if isinstance(pos, dict) is False:
        raise TypeError("Error, invalid pos parameter (not a dict).")
    if len(pos) != len(G):
        raise ValueError("Error, invalid pos parameter (not correct length).")
    for u in G:
        if u not in pos:
            raise ValueError("Error, node " + str(u) + " has no valid (x,y) "
                             "coordinate")
    posSet = {tuple(pos[u]) for u in G}
    if len(posSet) < len(pos):
        raise ValueError("Error, there are nodes in G with equal corrdinates")
    if nx.is_planar is False or nx.has_bridges(G):
        raise ValueError("Error, supplied graph is not bridge-free and planar")
    if embeddingIsPlanar(G, pos) is False:
        raise ValueError(
            "Error, supplied embedding has crossing edges. This could be due ",
            "to rounding errors when performing calculations on the node ",
            "coordinates")
    # Get the adjacency list of the embedding such that neighbours appear in
    # order of angle in an anticlockwise direction (zero degrees points 'East')
    adj = {}
    for u in G:
        L = [(getBearing(pos[u], pos[v]), v) for v in G[u]]
        L.sort()
        for i in range(len(L)-1):
            if L[i][0] == L[i+1][0]:
                raise ValueError("Error, two neighbors of node " + str(u) + " "
                                 "are on the same bearing. Invalid embedding")
        adj[u] = [x[1] for x in L]
    # For each node u, map each incoming arc (w,u) to the next outgoing arc in
    # (u,v) in clockwise order (u,v)
    inOutMap = {}
    for u in adj:
        for i in range(len(adj[u])):
            v = adj[u][i]
            w = adj[u][(i+1) % len(adj[u])]
            inOutMap[w, u] = (u, v)
    # Now identify each face of the embedding as a sequence of arcs
    faces = []
    while inOutMap:
        f = []
        firstArc = next(iter(inOutMap))
        arc = firstArc
        while True:
            f.append(arc)
            arc = inOutMap[arc]
            if arc == firstArc:
                break
        for arc in f:
            del inOutMap[arc]
        faces.append(f)
    # Next, identify the unique face that goes clockwise (this is the exterior
    # face) and set this as the first face
    for i in range(len(faces)):
        if isClockwise([pos[u] for u, _ in faces[i]]):
            break
    faces[0], faces[i] = faces[i], faces[0]
    # For each edge in G, identify the two faces it borders in the embedding
    borders = {frozenset({u, v}): [] for u, v in G.edges()}
    for i in range(len(faces)):
        for (u, v) in faces[i]:
            borders[frozenset({u, v})].append(i)
    # We can now make the dual graph H of G's embedding.
    H = nx.Graph()
    H.add_nodes_from([u for u in range(len(faces))])
    for edge in borders:
        H.add_edge(borders[edge][0], borders[edge][1])
    # Specify each face as a sequence of vertices, and return this with H
    faceNodes = [[u for (u, _) in f] for f in faces]
    return H, faceNodes

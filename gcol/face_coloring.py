"""Face coloring functions."""

import networkx as nx
import math
import itertools
from .node_coloring import node_k_coloring, node_coloring, _backtrackcol
from .node_coloring import equitable_node_k_coloring, node_precoloring
from .node_coloring import _check_params, node_list_coloring


def _canonical_node_rotation(S):
    # Takes a sequence of nodes S and rotates them so that the "minimum" node
    # is first. This gives a canonical ordering, which is returned as a tuple.
    # The minimum is found using a comparison by type, then by the string
    # representation of the value
    if not isinstance(S, (list, tuple)):
        raise ValueError(
            "Error, faces must be expressed as a list or tuple of nodes."
        )
    if not S:
        return S
    try:
        i = min(range(len(S)), key=lambda j: (type(S[j]).__name__, repr(S[j])))
        return tuple(S[i:] + S[:i])
    except TypeError:
        print("Error, list of nodes contains incompatible types.")


def _canonical_node_order(S):
    # Takes a sequence of nodes S and sorts them. This gives a canonical
    # ordering. As above, this is found via a comparison by type, then by the
    # string representation of the value
    try:
        return sorted(S, key=lambda v: (type(v).__name__, repr(v)))
    except TypeError:
        print("Error, list of nodes contains incompatible types.")


def dual_graph(G, pos):
    r"""Return the dual graph of the specified planar embedding of ``G``.

    The dual graph $G^*$ of a planar graph $G$ has a node for each face in
    the supplied embedding of $G$, including the external face. Each edge
    in $G^*$ corresponds to a pair of faces in $G$ that share a boundary.
    According to Euler's formula, $G$ has $f=m-n+2$ faces, where $n$ is its
    number of nodes and $m$ is the number of edges. Consequently, $G^*$ has
    $f$ nodes.

    The graph ``G`` must be planar. The embedding is defined by ``pos``,
    which should give valid $(x,y)$ coordinates for all nodes in ``G`` so
    that none of its edges (expressed as straight lines) cross. ``G`` should
    also be connected and have no bridges.

    Parameters
    ----------
    G : NetworkX graph
        A bridge-free, connected planar graph.

    pos : dict
        A dictionary of positions keyed by node. All positions should be
        $(x,y)$ coordinates, and none of the edges in the resultant embedding
        should be crossing.

    Returns
    -------
    NetworkX graph
        The dual graph in which nodes are labelled using integers from 0
        upwards. Node 0 corresponds to the single external face of ``G``; the
        remainder correspond to the internal faces.

    list
        The $i$th element in the list is a tuple giving the sequence of nodes
        that surround the $i$th face in ``G``. This face corresponds to node
        $i$ in the returned dual graph. The first element in this list
        defines the external face; the remainder define the internal faces.
        For internal faces, the nodes are listed in a counterclockwise order.
        For the external face, the nodes are listed in a clockwise order.

    Examples
    --------
    >>> import gcol
    >>> import networkx as nx
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> pos = nx.planar_layout(G)
    >>> H, faces = gcol.dual_graph(G, pos)
    >>> print(H)
    Graph with 12 nodes and 30 edges
    >>> print(faces)
    [(0, 10, 9, 8, 1), ..., (13, 12, 16, 15, 14)]

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

        If ``G`` is not connected or is a singleton.

    TypeError
        If ``pos`` is not a dictionary.

    ValueError
        If ``pos`` has missing or invalid entries.

        If ``pos`` does not specify a valid planar embedding of ``G``.

        If ``G`` is not planar or contains bridges.

    Notes
    -----
    The structure of a dual graph $G^*$ depends on the coordinates of the
    nodes in $G$. That is, different planar embeddings of $G$ can lead to
    different dual graphs.

    If the graph ``G`` contains no articulation points, all faces will be
    cycles. If ``G`` does contain any articulation points, these can occur
    more than once on the boundary of  a face; hence, some faces may be
    circuits.

    At present, this method does not allow self-loops, disconnected graphs
    (including faces with holes), or multi-edges. Multi-edges can be simulated
    by using paths of degree-two nodes with suitable coordinates.

    See Also
    --------
    face_chromatic_number
    face_coloring

    """

    def getBearing(P, Q):
        P, Q = tuple(P), tuple(Q)
        # Get the bearing of line PQ, where P and Q are both (x,y) coordinates.
        # b is rounded to 8 d.p. to avoid errors
        b = round(math.degrees(math.atan2(Q[1]-P[1], Q[0]-P[0])), 8)
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
        # Return true iff none of the edges in the embedding cross. First,
        # create a line for each edge, ensuring the leftmost endpoint is first
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

    # Check the supplied graph is connected and bridge free and that the
    # postions dictionary give a planar bridge-free embedding
    _check_params(G, "random", None, 0, 0)
    if len(G) == 0:
        return nx.Graph(), []
    if len(G) == 1:
        raise NotImplementedError("Error, supplied graph is a single node")
    if isinstance(pos, dict) is False:
        raise TypeError("Error, invalid pos parameter (not a dict).")
    if len(pos) != len(G):
        raise ValueError("Error, invalid pos parameter (not correct length).")
    for u in G:
        if u not in pos:
            raise ValueError("Error, node " + str(u) + " has no valid (x,y) "
                             "coordinate in pos parameter")
    posSet = {tuple(pos[u]) for u in G}
    if len(posSet) < len(pos):
        raise ValueError("Error, there are nodes in G with equal coordinates")
    if nx.is_connected(G) is False:
        raise NotImplementedError("Error, supplied graph is not connected")
    if nx.is_planar(G) is False or nx.has_bridges(G):
        raise ValueError("Error, supplied graph is not bridge-free and planar")
    if embeddingIsPlanar(G, pos) is False:
        raise ValueError(
            "Error, supplied embedding has crossing edges. This could be due ",
            "to rounding errors when performing calculations on the node ",
            "coordinates")
    # Make an adjacency list adj of G's embedding so that neighbors appear in
    # order of angle in counterclockwise direction (zero deg points 'East').
    # In adj, each edge {u,v} from G contributes two arcs, (u,v) and (v,u), so
    # the resultant digraph is Eulerian. Here, we loop over a sorted list of
    # nodes V to ensure one-to-one correspondence between G and adj (that is,
    # we do not depend on the order that the nodes were originally inserted
    # into G)
    counter = itertools.count()
    adj = {}
    for u in _canonical_node_order(G.nodes):
        L = [(getBearing(pos[u], pos[v]), next(counter), v) for v in G[u]]
        L.sort()
        for i in range(len(L)-1):
            if L[i][0] == L[i+1][0]:
                raise ValueError("Error, two neighbors of node " + str(u) + " "
                                 "are on the same bearing. Invalid embedding")
        adj[u] = [x[2] for x in L]
    # For each node u, map each incoming arc (w,u) to the next outgoing arc
    # (u,v) in clockwise order
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
    # Specify each face as a sequence of vertices, and return this alongside H
    faces = [_canonical_node_rotation([u for (u, _) in f]) for f in faces]
    return H, faces


def face_coloring(G, pos, strategy="dsatur", opt_alg=None, it_limit=0,
                  verbose=0):
    r"""Return a coloring of a planar graph's faces.

    A face coloring is an assignment of colors to the faces of a graph's planar
    embedding so that adjacent faces have different colors (a pair of faces is
    adjacent if and only if they share a bordering edge). The aim is to use as
    few colors as possible. Face colorings are only possible in planar
    embeddings; hence the graph ``G`` must be planar, and ``pos`` should give
    valid $(x,y)$ coordinates for all nodes.

    The smallest number of colors needed to face color a graph is known as its
    face chromatic number. According to the four color theorem [1]_, face
    colorings never require more than four colors. In this implementation, face
    colorings of a graph $G$ are determined by forming $G$'s dual graph, and
    then coloring the dual's nodes using the :meth:`node_coloring` method. All
    parameters are therefore the same as the latter. If $G$ has $n$ nodes and
    $m$ edges, its embedding has exactly $m-n+2$ faces, including the external
    face.

    Parameters
    ----------
    G : NetworkX graph
        A bridge-free, connected planar graph. Its faces will be colored.

    pos : dict
        A dictionary of positions keyed by node. All positions should be
        $(x,y)$ coordinates, and none of the edges in the resultant embedding
        should be crossing.

    strategy : string, optional (default='dsatur')
        A string specifying the method used to generate the initial solution.
        It must be one of the following:

        * ``'random'`` : Randomly orders the dual's nodes and then applies the
          greedy algorithm for graph node coloring [2]_.
        * ``'welsh-powell'`` : Orders the dual's nodes by decreasing degree,
          then applies the greedy algorithm.
        * ``'dsatur'`` : Uses the DSatur algorithm for graph node coloring on
          the dual [3]_.
        * ``'rlf'`` : Uses the recursive largest first (RLF) algorithm for
          graph node coloring on the dual [4]_.

    opt_alg : None or int, optional (default=None)
        An integer specifying the optimization method that will be used to try
        to reduce the number of colors. It must be one of the following

        * ``1`` : An exact, exponential-time algorithm based on backtracking.
          The algorithm halts only when an optimal solution has been found.
        * ``2`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing adjacent nodes in the dual to have the
          same color. Each iteration has a complexity $O(m + kn)$, where $n$ is
          the number of nodes in the dual, $m$ is the number of edges in the
          dual, and $k$ is the number of colors in the current solution.
        * ``3`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes in the dual to be uncolored.
          Each iteration has a complexity $O(m + kn)$, as above.
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
        A dictionary with keys representing faces and values representing their
        colors. Colors are identified by the integers $0,1,2,\ldots$. The
        number of colors being used in a solution ``c`` is therefore
        ``max(c.values()) + 1``. Each face (key) is a tuple that gives the
        sequence of nodes that surround it. The first element in ``c`` defines
        the external face; the remainder defines the internal faces. For
        internal faces, the nodes are listed in a counterclockwise order; for
        the external face, the nodes are listed in a clockwise order.

    Examples
    --------
    >>> import gcol
    >>> import networkx as nx
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> pos = nx.planar_layout(G)
    >>> c = gcol.face_coloring(G, pos)
    >>> print(c)
    {(1, 0, 10, 9, 8): 0, (10, 0, 19, 18, 11): 2, ..., (13, 12, 16, 15, 14): 2}

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

        If ``G`` is not connected or is a singleton.

    TypeError
        If ``pos`` is not a dictionary.

    ValueError
        If ``strategy`` is not among the supported options.

        If ``opt_alg`` is not among the supported options.

        If ``it_limit`` is not a nonnegative integer.

        If ``verbose`` is not a nonnegative integer.

        If ``pos`` has missing or invalid entries.

        If ``pos`` does not specify a valid planar embedding of ``G``.

        If ``G`` is not planar or contains bridges.

    Notes
    -----
    As mentioned, in this implementation face colorings of a graph $G$ are
    determined by forming its dual and then passing this to the
    :meth:`node_coloring` method. All details are therefore the same as those
    in the latter method, where they are documented more fully.

    All the above algorithms and bounds are described in detail in [5]_. The
    c++ code used in [5]_ and [6]_ forms the basis of this library's Python
    implementations.

    See Also
    --------
    face_chromatic_number
    :meth:`gcol.node_coloring.node_coloring`

    References
    ----------
    .. [1] Wikipedia: Four Color Theorem
      <https://en.wikipedia.org/wiki/Four_color_theorem>
    .. [2] Wikipedia: Greedy Coloring
      <https://en.wikipedia.org/wiki/Greedy_coloring>
    .. [3] Wikipedia: DSatur <https://en.wikipedia.org/wiki/DSatur>
    .. [4] Wikipedia: Recursive largest first (RLF) algorithm
      <https://en.wikipedia.org/wiki/Recursive_largest_first_algorithm>
    .. [5] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
      Applications (second ed.). Springer. ISBN: 978-3-030-81053-5.
      <https://link.springer.com/book/10.1007/978-3-030-81054-2>.
    .. [6] Lewis, R: Graph Colouring Algorithm User Guide
      <https://rhydlewis.eu/gcol/>

    """
    _check_params(G, strategy, opt_alg, it_limit, verbose)
    if len(G) == 0:
        return {}
    # Color the nodes of the dual graph H of the emedding defined by G and pos
    H, faces = dual_graph(G, pos)
    c = node_coloring(
        H, strategy=strategy,
        opt_alg=opt_alg,
        it_limit=it_limit,
        verbose=verbose
    )
    # Return the face coloring of G.
    return {tuple(faces[i]): c[i] for i in range(len(H))}


def face_chromatic_number(G):
    r"""Return the face chromatic number of the planar graph ``G``.

    The face chromatic number of a planar graph $G$ is the minimum number of
    colors needed to color its faces so that no two adjacent faces have the
    same color (a pair of faces is considered adjacent if and only if they
    share a common bordering edge). According to the four color theorem [1]_,
    it will never exceed four.

    The approach used here is based on the backtracking algorithm of [2]_. This
    is exact but operates in exponential time in the worst case. In this
    implementation, the solution is found for $G$ by determining a planar
    embedding, forming the dual graph, and then passing this to the
    :meth:`chromatic_number` method.

    Parameters
    ----------
    G : NetworkX graph
        The face chromatic number for this graph will be calculated. It
        must be bridge-free, connected, and planar.

    Returns
    -------
    int
        A nonnegative integer that gives the face chromatic number of ``G``.

    Examples
    --------
    >>> import gcol
    >>> import networkx as nx
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> print(gcol.face_chromatic_number(G))
    4

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

        If ``G`` is not connected or is a singleton.

    ValueError
        If ``G`` is not planar or has bridges.

    Notes
    -----
    The backtracking approach used here is an implementation of the exact
    algorithm described in [2]_. It has exponential runtime and halts only when
    the face chromatic number has been determined. Further details of this
    algorithm are given in the notes section of the :meth:`node_coloring`
    method.

    The above algorithm is described in detail in [2]_. The c++ code used in
    [2]_ and [3]_ forms the basis of this library's Python implementations.

    See Also
    --------
    face_coloring
    :meth:`gcol.node_coloring.chromatic_number`

    References
    ----------
    .. [1] Wikipedia: Four Color Theorem
      <https://en.wikipedia.org/wiki/Four_color_theorem>
    .. [2] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
      Applications (second ed.). Springer. ISBN: 978-3-030-81053-5.
      <https://link.springer.com/book/10.1007/978-3-030-81054-2>.
    .. [3] Lewis, R: Graph Colouring Algorithm User Guide
      <https://rhydlewis.eu/gcol/>

    """
    if G.is_directed() or G.is_multigraph() or nx.number_of_selfloops(G) > 0:
        raise NotImplementedError(
            "Error, this method cannot be used with directed graphs "
            "multigraphs, or graphs with self-loops."
        )
    if len(G) == 0:
        return 0
    H, faces = dual_graph(G, nx.planar_layout(G))
    cliqueNum = nx.approximation.large_clique_size(H)
    c = _backtrackcol(H, cliqueNum, 0)
    return max(c.values()) + 1


def face_k_coloring(G, pos, k, opt_alg=None, it_limit=0, verbose=0):
    r"""Attempt to color the faces of a planar graph ``G`` using ``k`` colors.

    This is done so that adjacent faces have different colors (a pair of faces
    is adjacent if and only if they share a bordering edge). The graph ``G``
    must be planar, and ``pos`` should give valid $(x,y)$ coordinates for all
    nodes.

    According to the four color theorem [1]_, face colorings never require
    more than four colors. In this implementation, face colorings of a graph
    $G$ are determined by forming $G$'s dual graph, and then coloring the
    dual's nodes using the :meth:`node_k_coloring` method. All parameters are
    therefore the same as the latter. If $G$ has $n$ nodes and $m$ edges, its
    embedding has exactly $m-n+2$ faces, including the external face.

    If a face $k$-coloring cannot be determined by the algorithm, a
    ``ValueError`` exception is raised. Otherwise, a face $k$-coloring is
    returned.

    Parameters
    ----------
    G : NetworkX graph
        A bridge-free, connected planar graph. Its faces will be colored.

    k : int
        The number of colors to use.

    pos : dict
        A dictionary of positions keyed by node. All positions should be
        $(x,y)$ coordinates, and none of the edges in the resultant embedding
        should be crossing.

    opt_alg : None or int, optional (default=None)
        An integer specifying the optimization method that will be used to try
        to reduce the number of colors. It must be one of the following

        * ``1`` : An exact, exponential-time algorithm based on backtracking.
          The algorithm halts only when an optimal solution has been found.
        * ``2`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing adjacent nodes in the dual to have the
          same color. Each iteration has a complexity $O(m + kn)$, where $n$ is
          the number of nodes in the dual, $m$ is the number of edges in the
          dual, and $k$ is the number of colors in the current solution.
        * ``3`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes in the dual to be uncolored.
          Each iteration has a complexity $O(m + kn)$, as above.
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
        A dictionary with keys representing faces and values representing their
        colors. Colors are identified by the integers $0,1,2,\ldots$. The
        number of colors being used in a solution ``c`` is therefore
        ``max(c.values()) + 1``. Each face (key) is a tuple that gives the
        sequence of nodes that surround it. he first element in ``c`` defines
        the external face; the remainder defines the internal faces. For
        internal faces, the nodes are listed in a counterclockwise order; for
        the external face, the nodes are listed in a clockwise order.

    Examples
    --------
    >>> import gcol
    >>> import networkx as nx
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> pos = nx.planar_layout(G)
    >>> c = gcol.face_k_coloring(G, pos, 5)
    >>> print(c)
    {(1, 0, 10, 9, 8): 0, (10, 0, 19, 18, 11): 2, ..., (13, 12, 16, 15, 14): 0}

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

        If ``G`` is not connected or is a singleton.

    TypeError
        If ``pos`` is not a dictionary.

    ValueError
        If ``opt_alg`` is not among the supported options.

        If ``it_limit`` is not a nonnegative integer.

        If ``verbose`` is not a nonnegative integer.

        If ``pos`` has missing or invalid entries.

        If ``pos`` does not specify a valid planar embedding of ``G``.

        If ``G`` is not planar or contains bridges.

        If ``k`` is not a nonnegative integer.

        If a clique larger than ``k`` is observed in the dual graph of $G$.

        If a face $k$-coloring could not be determined.

    Notes
    -----
    As mentioned, in this implementation face colorings of a graph $G$ are
    determined by forming its dual and then passing this to the
    :meth:`node_k_coloring` method. All details are therefore the same as those
    in the latter method, where they are documented more fully. The routine
    halts immediately once a face $k$-coloring has been achieved.

    All the above algorithms and bounds are described in detail in [2]_. The
    c++ code used in [2]_ and [3]_ forms the basis of this library's Python
    implementations.

    See Also
    --------
    face_coloring
    :meth:`gcol.node_coloring.node_k_coloring`

    References
    ----------
    .. [1] Wikipedia: Four Color Theorem
      <https://en.wikipedia.org/wiki/Four_color_theorem>
    .. [2] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
      Applications (second ed.). Springer. ISBN: 978-3-030-81053-5.
      <https://link.springer.com/book/10.1007/978-3-030-81054-2>.
    .. [3] Lewis, R: Graph Colouring Algorithm User Guide
      <https://rhydlewis.eu/gcol/>

    """
    _check_params(G, "dstaur", opt_alg, it_limit, verbose)
    if k < 0:
        raise ValueError("Error, positive integer needed for k")
    if len(G) == 0:
        return {}
    H, faces = dual_graph(G, pos)
    c = node_k_coloring(
        H, k, opt_alg=opt_alg, it_limit=it_limit, verbose=verbose
    )
    return {tuple(faces[i]): c[i] for i in range(len(H))}


def equitable_face_k_coloring(G, pos, k, opt_alg=None, it_limit=0, verbose=0):
    r"""Attempt to color the faces of a planar graph ``G`` using ``k`` colors.

    This is done so that (a) adjacent faces have different colors, and (b) the
    number of faces with each color is equal. (A pair of faces is adjacent if
    and only if they share a bordering edge.) The graph ``G`` must be planar,
    and ``pos`` should give valid $(x,y)$ coordinates for all nodes.

    This method first follows the steps used by the :meth:`face_k_coloring`
    method. All parameters are therefore the same as the latter. If a face
    $k$-coloring cannot be determined by the algorithm, a ``ValueError``
    exception is raised. Otherwise, once a face $k$-coloring has been formed,
    the algorithm uses a bespoke local search operator to reduce the standard
    deviation in the number of faces in each color class.

    In solutions returned by this method, adjacent faces always receive
    different colors; however, the coloring is not guaranteed to be equitable,
    even if an equitable face $k$-coloring exists.

    According to the four color theorem [1]_, face colorings never require more
    than four colors. In this implementation, face colorings of a graph $G$ are
    determined by forming $G$'s dual graph.

    Parameters
    ----------
    G : NetworkX graph
        A bridge-free, connected planar graph. Its faces will be colored.

    k : int
        The number of colors to use.

    pos : dict
        A dictionary of positions keyed by node. All positions should be
        $(x,y)$ coordinates, and none of the edges in the resultant embedding
        should be crossing.

    opt_alg : None or int, optional (default=None)
        An integer specifying the optimization method that will be used to try
        to reduce the number of colors. It must be one of the following

        * ``1`` : An exact, exponential-time algorithm based on backtracking.
          The algorithm halts only when an optimal solution has been found.
        * ``2`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing adjacent nodes in the dual to have the
          same color. Each iteration has a complexity $O(m + kn)$, where $n$ is
          the number of nodes in the dual, $m$ is the number of edges in the
          dual, and $k$ is the number of colors in the current solution.
        * ``3`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes in the dual to be uncolored.
          Each iteration has a complexity $O(m + kn)$, as above.
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
        A dictionary with keys representing faces and values representing their
        colors. Colors are identified by the integers $0,1,2,\ldots$. The
        number of colors being used in a solution ``c`` is therefore
        ``max(c.values()) + 1``. Each face (key) is a tuple that gives the
        sequence of nodes that surround it. The first element in ``c`` defines
        the external face; the remainder defines the internal faces. For
        internal faces, the nodes are listed in a counterclockwise order; for
        the external face, the nodes are listed in a clockwise order.

    Examples
    --------
    >>> import gcol
    >>> import networkx as nx
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> pos = nx.planar_layout(G)
    >>> c = gcol.equitable_face_k_coloring(G, pos, 5)
    >>> print(c)
    {(1, 0, 10, 9, 8): 0, (10, 0, 19, 18, 11): 2, ..., (13, 12, 16, 15, 14): 0}

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

        If ``G`` is not connected or is a singleton.

    TypeError
        If ``pos`` is not a dictionary.

    ValueError
        If ``opt_alg`` is not among the supported options.

        If ``it_limit`` is not a nonnegative integer.

        If ``verbose`` is not a nonnegative integer.

        If ``pos`` has missing or invalid entries.

        If ``pos`` does not specify a valid planar embedding of ``G``.

        If ``G`` is not planar or contains bridges.

        If ``k`` is not a nonnegative integer.

        If a clique larger than ``k`` is observed in the dual graph of $G$.

        If a face $k$-coloring could not be determined.

    Notes
    -----
    As mentioned, in this implementation face colorings of a graph $G$ are
    determined by forming its dual and then passing this to the
    :meth:`node_k_coloring` method. If a face $k$-coloring is achieved, a
    bespoke local search operator (based on steepest descent) is then used to
    try to reduce the standard deviation in sizes across the $k$ color classes.
    This follows the same steps as the :meth:`equitable_node_k_coloring`
    method, using the dual of ``G``. Further details on this optimization
    method can be found in Chapter 7 of [2]_.

    All the above algorithms and bounds are described in detail in [2]_. The
    c++ code used in [2]_ and [3]_ forms the basis of this library's Python
    implementations.

    See Also
    --------
    face_coloring
    :meth:`gcol.node_coloring.equitable_node_k_coloring`

    References
    ----------
    .. [1] Wikipedia: Four Color Theorem
      <https://en.wikipedia.org/wiki/Four_color_theorem>
    .. [2] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
      Applications (second ed.). Springer. ISBN: 978-3-030-81053-5.
      <https://link.springer.com/book/10.1007/978-3-030-81054-2>.
    .. [3] Lewis, R: Graph Colouring Algorithm User Guide
      <https://rhydlewis.eu/gcol/>

    """
    _check_params(G, "dsatur", opt_alg, it_limit, verbose)
    if k < 0:
        raise ValueError("Error, nonnegative integer needed for k")
    if len(G) == 0:
        return {}
    H, faces = dual_graph(G, pos)
    c = equitable_node_k_coloring(
        H, k, weight=None, opt_alg=opt_alg, it_limit=it_limit, verbose=verbose
    )
    return {tuple(faces[i]): c[i] for i in range(len(H))}


def face_precoloring(
    G, pos, precol=None, strategy="dsatur", opt_alg=None, it_limit=0, verbose=0
):
    r"""Give a face coloring of a planar graph where some faces are precolored.

    A face coloring is an assignment of colors to the faces of a graph's
    planar embedding so that adjacent faces have different colors. In the
    face precoloring problem, some of the faces have already been assigned
    colors. Colors are defined using labels belonging to the set
    $\{0,1,2,\ldots\}$. Assuming $k$ is the largest color label used in the
    precoloring, the aim is to color all remaining faces using $l$ colors,
    where $l$ is minimized and $k\leq l$.

    Face colorings are only possible in planar embeddings; hence the graph
    ``G`` must be planar, and ``pos`` should give valid $(x,y)$ coordinates
    for all nodes.

    In this implementation, face colorings of a graph $G$ are determined by
    forming $G$'s dual graph, and then passing the dual to the
    :meth:`node_precoloring` method. All parameters are therefore the same as
    the latter.

    Parameters
    ----------
    G : NetworkX graph
        A bridge-free, connected planar graph. Its faces will be colored.

    pos : dict
        A dictionary of positions keyed by node. All positions should be
        $(x,y)$ coordinates, and none of the edges in the resultant embedding
        should be crossing.

    precol : None or dict, optional (default=None)
        A dictionary, keyed by faces, that specifies the colors of the
        precolored faces. Faces are identified using a tuple of nodes.
        Each internal face is characterized by the series of nodes that
        surround it in a counterclockwise direction; the one
        external face is identified by the series of nodes, traveling in
        a clockwise direction.

    strategy : string, optional (default='dsatur')
        A string specifying the method used to generate the initial solution.
        It must be one of the following:

        * ``'random'`` : Randomly orders the dual's nodes and then applies the
          greedy algorithm for graph node coloring [1]_.
        * ``'welsh-powell'`` : Orders the dual's nodes by decreasing degree,
          then applies the greedy algorithm.
        * ``'dsatur'`` : Uses the DSatur algorithm for graph node coloring on
          the dual [2]_.
        * ``'rlf'`` : Uses the recursive largest first (RLF) algorithm for
          graph node coloring on the dual [3]_.

    opt_alg : None or int, optional (default=None)
        An integer specifying the optimization method that will be used to try
        to reduce the number of colors. It must be one of the following

        * ``1`` : An exact, exponential-time algorithm based on backtracking.
          The algorithm halts only when an optimal solution has been found.
        * ``2`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing adjacent nodes in the dual to have the
          same color. Each iteration has a complexity $O(m + kn)$, where $n$ is
          the number of nodes in the dual, $m$ is the number of edges in the
          dual, and $k$ is the number of colors in the current solution.
        * ``3`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes in the dual to be uncolored.
          Each iteration has a complexity $O(m + kn)$, as above.
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
        A dictionary with keys representing faces and values representing their
        colors. Colors are identified by the integers $0,1,2,\ldots$. Each
        face (key) is a tuple that gives the sequence of nodes that surround
        it. The first element in ``c`` defines the external face; the remainder
        define the internal faces. For internal faces, the nodes are listed in
        a counterclockwise order; for the external face, the nodes are listed
        in a clockwise order.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> pos = nx.planar_layout(G)
    >>> precol = {(0, 10, 9, 8, 1): 0, (6, 5, 4, 3, 2): 1}
    >>> c = gcol.face_precoloring(G, pos, precol)
    >>> print(c)
    {(0, 10, 9, 8, 1): 0, (0, 19, 18, 11, 10): 1,..., (2, 6, 5, 4, 3): 1}

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

        If ``G`` is not connected or is a singleton.

    TypeError
        If ``pos`` is not a dictionary.

    ValueError
        If ``strategy`` is not among the supported options.

        If ``opt_alg`` is not among the supported options.

        If ``it_limit`` is not a nonnegative integer.

        If ``verbose`` is not a nonnegative integer.

        If ``precol`` contains a face that is not in the embedding of ``G``.

        If ``precol`` contains a color label that is not a nonnegative integer.

        If ``precol`` contains a pair of adjacent faces assigned to the same
        color.

        If ``pos`` has missing or invalid entries.

        If ``pos`` does not specify a valid planar embedding of ``G``.

        If ``G`` is not planar or contains bridges.

    TypeError
        If ``precol`` is not a dict.

    Notes
    -----
    As mentioned, in this implementation face colorings of a graph $G$ are
    determined by forming its dual and then passing this to the
    :meth:`node_precoloring` method. All details are therefore the same as
    those in the latter method, where they are documented more fully.

    All the above algorithms and bounds are described in detail in [4]_. The
    c++ code used in [4]_ and [5]_ forms the basis of this library's Python
    implementations.

    See Also
    --------
    face_coloring
    dual_graph
    :meth:`gcol.node_coloring.node_precoloring`

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
    .. [5] Lewis, R: Graph Colouring Algorithm User Guide
      <https://rhydlewis.eu/gcol/>

    """
    _check_params(G, strategy, opt_alg, it_limit, verbose)
    if len(G) == 0:
        return {}
    if precol is None or precol == {}:
        return face_coloring(
            G, pos, strategy=strategy, opt_alg=opt_alg, it_limit=it_limit,
            verbose=verbose
        )
    if not isinstance(precol, dict):
        raise TypeError(
            "Error, the precoloring should be a dict that assigns a subset of "
            "the graph emebdding's faces to colors"
        )
    H, faces = dual_graph(G, pos)
    # Rotate faces in precol to their canonical form, matching those in H
    precol_canon = {_canonical_node_rotation(f): precol[f] for f in precol}
    faces_set = set(faces)
    for f in precol_canon:
        if f not in faces_set:
            raise ValueError(
                "Error, a face is defined in the precoloring that is not in "
                "the graph embedding defined by G and pos."
            )
        if not isinstance(precol_canon[f], int) or precol_canon[f] < 0:
            raise ValueError(
                "Error, all color labels in the precoloring should be "
                "nonnegative integers."
            )
    P = {i: precol_canon[faces[i]]
         for i in range(len(faces)) if faces[i] in precol_canon}
    c = node_precoloring(
        H, P, strategy=strategy, opt_alg=opt_alg, it_limit=it_limit,
        verbose=verbose
    )
    return {tuple(faces[i]): c[i] for i in range(len(H))}


def face_list_coloring(
    G,
    pos,
    allowed_cols=None,
    strategy="dsatur",
    opt_alg=None,
    it_limit=0,
    verbose=0
):
    r"""Return a solution to the face list coloring problem on ``G``.

    A face coloring is an assignment of colors to the faces of a graph's
    planar embedding so that adjacent faces have different colors. In the face
    list coloring problem, each face $f$ is associated with a list of allowed
    colors $L(f)$. A solution is an assignment of colors to all faces so that
    adjacent faces have different colors, and the color of each face $f$
    belongs to the list $L(f)$.

    Face colorings are only possible in planar embeddings; hence the graph
    ``G`` must be planar, and ``pos`` should give valid $(x,y)$ coordinates
    for all nodes.

    Here, colors are defined using labels belonging to $\{0,1,2,\ldots\}$.
    Assuming $k$ is the largest color label appearing across all lists, the aim
    is to find a solution using at most $k$ colors. If this cannot be done,
    an exception is raised (see below).

    In this implementation, face colorings of a graph $G$ are determined by
    forming $G$'s dual graph, and then passing the dual to the
    :meth:`node_list_coloring` method. All parameters are therefore the same as
    the latter.

    Parameters
    ----------
    G : NetworkX graph
        A bridge-free, connected planar graph. Its faces will be colored.

    pos : dict
        A dictionary of positions keyed by node. All positions should be
        $(x,y)$ coordinates, and none of the edges in the resultant embedding
        should be crossing.

    allowed_cols : None or dict, optional (default=None)
        A dictionary, keyed by faces, that specifies the allowed colors of each
        face. Faces are identified using a tuple of nodes. Each internal face
        is characterized by the series of nodes that surround it in a
        counterclockwise direction; the one external face is identified by the
        series of nodes, traveling in a clockwise direction. Each value in
        ``allowed_cols`` should be a list of (nonnegative integer)
        colors that give the permissible colors for the corresponding face.
        If None, a face coloring with the minimum number of colors is returned.

    strategy : string, optional (default='dsatur')
        A string specifying the method used to generate the initial solution.
        It must be one of the following:

        * ``'random'`` : Randomly orders the dual's nodes and then applies the
          greedy algorithm for graph node coloring [1]_.
        * ``'welsh-powell'`` : Orders the dual's nodes by decreasing degree,
          then applies the greedy algorithm.
        * ``'dsatur'`` : Uses the DSatur algorithm for graph node coloring on
          the dual [2]_.
        * ``'rlf'`` : Uses the recursive largest first (RLF) algorithm for
          graph node coloring on the dual [3]_.

    opt_alg : None or int, optional (default=None)
        An integer specifying the optimization method that will be used.

        * ``1`` : An exact, exponential-time algorithm based on backtracking.
          The algorithm halts only when an optimal solution has been found.
        * ``2`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing adjacent nodes in the dual to have the
          same color. Each iteration has a complexity $O(m + kn)$, where $n$ is
          the number of nodes in the dual, $m$ is the number of edges in the
          dual, and $k$ is the number of colors in the current solution.
        * ``3`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes in the dual to be uncolored.
          Each iteration has a complexity $O(m + kn)$, as above.
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
        A dictionary with keys representing faces and values representing their
        colors. Colors are identified by the integers $0,1,2,\ldots$. Each
        face (key) is a tuple that gives the sequence of nodes that surround
        it. The first element in ``c`` defines the external face; the remainder
        define the internal faces. For internal faces, the nodes are listed in
        a counterclockwise order; for the external face, the nodes are listed
        in a clockwise order. Keys in the dict are rotated so that the node
        with minimal label appears first.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.cycle_graph(4)
    >>> G.add_edge(0, 2)
    >>> pos = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}
    >>> F = {(0, 3, 2, 1): [0, 1], (0, 2, 3): [0, 2], (2, 0, 1): [0]}
    >>> c = gcol.face_list_coloring(G, pos, F)
    >>> print(c)
    {(0, 3, 2, 1): 1, (0, 2, 3): 2, (0, 1, 2): 0}

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

        If ``allowed_cols`` has a face not in the calculated embedding of
        ``G``.

        If ``allowed_cols`` contains a color label that is not a nonnegative
        integer.

        If ``allowed_cols`` contains a pair of adjacent faces that have the
        same single allowed color.

        If a face list k-coloring could not be determined (the lists of
        allowed colors are too restrictive).

    TypeError
        If ``allowed_cols`` is not a dict.

    Notes
    -----
    All the above algorithms and bounds are described in detail in [1]. The c++
    code used in [1]_ and [5]_ forms the basis of this library's Python
    implementations.

    See Also
    --------
    :meth:`gcol.node_coloring.node_coloring`
    :meth:`gcol.node_coloring.node_list_coloring`
    face_coloring

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
    if allowed_cols is None or allowed_cols == {}:
        return face_coloring(
            G, pos, strategy=strategy, opt_alg=opt_alg, it_limit=it_limit,
            verbose=verbose
        )
    if not isinstance(allowed_cols, dict):
        raise TypeError(
            "Error, allowed_cols should be a dict specifying a set of "
            "allowed colors for every face in the calculated embedding of G."
        )
    H, faces = dual_graph(G, pos)
    if len(H) != len(allowed_cols):
        raise ValueError(
            "Error, a list of allowed colors must be specified for every face "
            "in the calculated planar embedding of G."
        )
    ac_canon = {_canonical_node_rotation(f): allowed_cols[f]
                for f in allowed_cols}
    for i in range(len(H)):
        if faces[i] not in ac_canon:
            raise ValueError(
                "Error, a face exists in the calculated planar embedding of "
                "G that is not present in allowed_cols."
            )
    face_allowed_cols = {}
    for i in range(len(H)):
        face_allowed_cols[i] = ac_canon[faces[i]]
    c = node_list_coloring(
        H, face_allowed_cols, strategy=strategy, opt_alg=opt_alg,
        it_limit=it_limit, verbose=verbose
    )
    return {tuple(faces[i]): c[i] for i in range(len(H))}


# Alternative spellings of the above methods
face_colouring = face_coloring
face_k_colouring = face_k_coloring
face_precolouring = face_precoloring
equitable_face_k_colouring = equitable_face_k_coloring
face_list_colouring = face_list_coloring

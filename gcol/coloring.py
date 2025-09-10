import gcol.equitable_node_coloring as enc
import gcol.node_coloring as nc
import gcol.face_coloring as fc
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from collections import deque
from collections import defaultdict
import random

tableau = {
    -1: (1.00, 1.00, 1.00), 0: (0.12, 0.46, 0.70), 1: (0.68, 0.78, 0.91),
    2: (1.00, 0.50, 0.05), 3: (1.00, 0.73, 0.47), 4: (0.17, 0.63, 0.17),
    5: (0.59, 0.87, 0.54), 6: (0.84, 0.15, 0.16), 7: (1.00, 0.59, 0.59),
    8: (0.58, 0.40, 0.74), 9: (0.77, 0.69, 0.83), 10: (0.55, 0.34, 0.29),
    11: (0.77, 0.61, 0.58), 12: (0.89, 0.46, 0.76), 13: (0.96, 0.71, 0.82),
    14: (0.50, 0.50, 0.50), 15: (0.78, 0.78, 0.78), 16: (0.73, 0.74, 0.13),
    17: (0.86, 0.86, 0.55), 18: (0.09, 0.74, 0.81), 19: (0.62, 0.85, 0.89)
}

colorful = {
    -1: (1.00, 1.00, 1.00), 0: (1.00, 0.00, 0.00), 1: (0.00, 1.00, 0.00),
    2: (0.00, 0.00, 1.00), 3: (1.00, 1.00, 0.00), 4: (1.00, 0.00, 1.00),
    5: (0.00, 1.00, 1.00), 6: (0.00, 0.00, 0.00), 7: (0.50, 0.00, 0.00),
    8: (0.00, 0.50, 0.00), 9: (0.00, 0.00, 0.50), 10: (0.50, 0.50, 0.00),
    11: (0.50, 0.00, 0.50), 12: (0.00, 0.50, 0.50), 13: (0.50, 0.50, 0.50),
    14: (0.75, 0.00, 0.00), 15: (0.00, 0.75, 0.00), 16: (0.00, 0.00, 0.75),
    17: (0.75, 0.75, 0.00), 18: (0.75, 0.00, 0.75), 19: (0.00, 0.75, 0.75),
    20: (0.75, 0.75, 0.75), 21: (0.25, 0.00, 0.00), 22: (0.00, 0.25, 0.00),
    23: (0.00, 0.00, 0.25), 24: (0.25, 0.25, 0.00), 25: (0.25, 0.00, 0.25),
    26: (0.00, 0.25, 0.25), 27: (0.25, 0.25, 0.25), 28: (0.13, 0.00, 0.00),
    29: (0.00, 0.13, 0.00), 30: (0.00, 0.00, 0.13), 31: (0.13, 0.13, 0.00),
    32: (0.13, 0.00, 0.13), 33: (0.00, 0.13, 0.13), 34: (0.13, 0.13, 0.13),
    35: (0.38, 0.00, 0.00), 36: (0.00, 0.38, 0.00), 37: (0.00, 0.00, 0.38),
    38: (0.38, 0.38, 0.00), 39: (0.38, 0.00, 0.38), 40: (0.00, 0.38, 0.38),
    41: (0.38, 0.38, 0.38), 42: (0.63, 0.00, 0.00), 43: (0.00, 0.63, 0.00),
    44: (0.00, 0.00, 0.63), 45: (0.63, 0.63, 0.00), 46: (0.63, 0.00, 0.63),
    47: (0.00, 0.63, 0.63), 48: (0.63, 0.63, 0.63), 49: (0.88, 0.00, 0.00),
    50: (0.00, 0.88, 0.00), 51: (0.00, 0.00, 0.88), 52: (0.88, 0.88, 0.00),
    53: (0.88, 0.00, 0.88), 54: (0.00, 0.88, 0.88), 55: (0.88, 0.88, 0.88)
}

colorblind = {
    -1: (1.00, 1.00, 1.00), 0: (0.00, 0.42, 0.64), 1: (1.00, 0.50, 0.05),
    2: (0.67, 0.67, 0.67), 3: (0.35, 0.35, 0.35), 4: (0.37, 0.62, 0.82),
    5: (0.78, 0.32, 0.00), 6: (0.54, 0.54, 0.54), 7: (0.64, 0.78, 0.93),
    8: (1.00, 0.74, 0.47), 9: (0.81, 0.81, 0.81)
}


def _check_params(G, strategy, opt_alg, it_limit, verbose):
    greedy_methods = {"random", "welsh_powell", "dsatur", "rlf"}
    opt_methods = {1, 2, 3, None}
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


def _all_numeric(L):
    # Returns True iff all items in the list are numeric values
    return all(isinstance(x, (int, float)) for x in L)


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


def partition(c):
    """Convert a coloring into its equivalent partition-based representation.

    Negative color labels (signifying uncolored nodes/edges) are ignored.

    Parameters
    ----------
    c : dict
        A dictionary with keys representing nodes or edges and values
        representing their colors. Colors are identified by the integers
        $0,1,2,\\ldots$.

    Returns
    -------
    list
        A list in which each element is a list containing the nodes/edges
        assigned to a particular color.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.node_coloring(G)
    >>> print(gcol.partition(c))
    [[0, 2, 8, 18, 4, 13, 15], ..., [3, 9, 11, 7, 5, 16]]
    >>>
    >>> c = gcol.edge_coloring(G)
    >>> print(gcol.partition(c))
    [[(11, 12), (18, 19), (16, 17), ..., (2, 6), (4, 5)]]

    Notes
    -----
    If all nodes in a color class are named by numerical values, the nodes are
    sorted in ascending order. Otherwise, the nodes of each color class are
    sorted by their string equivalents.

    See Also
    --------
    equitable_node_k_coloring
    equitable_edge_k_coloring

    """
    if len(c) == 0:
        return []
    k = max(c.values()) + 1
    S = [[] for i in range(k)]
    for v in c:
        if c[v] >= 0:
            S[c[v]].append(v)
    for i in range(k):
        if _all_numeric(S[i]):
            S[i].sort()
        else:
            S[i] = sorted(S[i], key=str)
    return S


def coloring_layout(G, c):
    """Arrange the nodes of the graph in a circle.

    Nodes of the same color are put next to each other. This method is designed
    to be used with the ``pos`` argument in the drawing functions of NetworkX
    (see example below).

    Parameters
    ----------
    G : NetworkX graph
        The graph we want to visualize.

    c : dict
        A dictionary with keys representing nodes and values representing
        their colors. Colors are identified by the integers $0,1,2,\\ldots$.
        Nodes with negative values are ignored.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node.

    Examples
    --------
    >>> import networkx as nx
    >>> import matplotlib.pyplot as plt
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.node_coloring(G)
    >>> nx.draw_networkx(
    ...     G, pos=gcol.coloring_layout(G, c),
    ...     node_color=gcol.get_node_colors(G, c)
    ... )
    >>> plt.show()

    See Also
    --------
    get_node_colors
    multipartite_layout

    """
    GCopy = nx.Graph()
    P = partition(c)
    for i in range(len(P)):
        for v in P[i]:
            GCopy.add_node(v)
    for u, v in G.edges():
        GCopy.add_edge(u, v)
    return nx.circular_layout(GCopy)


def multipartite_layout(G, c):
    """Arrange the nodes of the graph into columns.

    Nodes of the same color are put in the same column. This method is  used
    with the ``pos`` argument in the drawing functions of NetworkX (see
    example below).

    Parameters
    ----------
    G : NetworkX graph
        The graph we want to visualize.

    c : dict
        A dictionary with keys representing nodes and values representing
        their colors. Colors are identified by the integers $0,1,2,\\ldots$.
        Nodes with negative color labels are ignored.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node.

    Examples
    --------
    >>> import networkx as nx
    >>> import matplotlib.pyplot as plt
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.node_coloring(G)
    >>> nx.draw_networkx(
    ...     G, pos=gcol.multipartite_layout(G, c),
    ...     node_color=gcol.get_node_colors(G, c)
    ... )
    >>> plt.show()

    See Also
    --------
    get_node_colors
    coloring_layout

    """
    GCopy = nx.Graph()
    P = partition(c)
    for i in range(len(P)):
        for v in P[i]:
            GCopy.add_node(v, layer=i)
    for u, v in G.edges():
        GCopy.add_edge(u, v)
    return nx.multipartite_layout(GCopy, subset_key="layer")


def get_node_colors(G, c, palette=None):
    """Generate an RGB color for each node in the graph ``G``.

    The RGB color of a node is determined by its color label in ``c`` and the
    chosen palette. This method is designed to be used with the ``node_color``
    argument in the drawing functions of NetworkX (see example below). If a
    node is marked as uncolored (i.e., assigned a value of ``-1``, or is not
    present in ``c``), it is painted white.

    Parameters
    ----------
    G : NetworkX graph
        The graph we want to visualize.

    c : dict
        A dictionary with keys representing nodes and values representing their
        colors. Colors are identified by the integers $0,1,2,\\ldots$.

    palette : None or dict, optional (default=None)
        A dictionary that maps the integers $-1,0,1,\\ldots$ to RGB values.
        The in-built options are as follows

        * ``gcol.tableau`` : A collection of 21 colors provided by Tableau.
        * ``gcol.colorful`` : A collection of 57 bright colors that are
          chosen to contrast each other as much as possible.
        * ``gcol.colorblind`` : A collection of 11 colors, provided by
          Tableau, that are intended to help colorblind users.
        * If ``None``, then ``gcol.tableau`` is used.

    Returns
    -------
    list
        A sequence of RGB colors in node order.

    Examples
    --------
    >>> import networkx as nx
    >>> import matplotlib.pyplot as plt
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.node_coloring(G)
    >>> nx.draw_networkx(
    ...     G, pos=nx.spring_layout(G), node_color=gcol.get_node_colors(G, c)
    ... )
    >>> plt.show()

    Raises
    ------
    ValueError
        If ``c`` uses more colors than available in the palette.

    Notes
    -----
    User generated palettes can also be passed into this method. In such cases
    it is good practice to map the value ``-1`` to the color white.
    Descriptions on how to specify valid colors can be found at [1]_.

    See Also
    --------
    get_set_colors
    get_edge_colors
    get_face_colors

    References
    ----------
    .. [1] Matplotlib: Specifying colors
      <https://matplotlib.org/stable/users/explain/colors/colors.html>

    """
    if palette is None:
        palette = tableau
    if len(c) == 0:
        return [palette[-1] for v in G]
    if max(c.values()) + 1 > len(palette) - 1:
        raise ValueError(
            "Error, insufficient colors are available in the chosen palette"
        )
    return [palette[c[v]] if v in c else palette[-1] for v in G]


def get_edge_colors(G, c, palette=None):
    """Generate an RGB color for each edge in the graph ``G``.

    The RGB color of an edge is determined by its color label in ``c`` and the
    chosen palette. This method is designed to be used with the ``edge_color``
    argument in the drawing functions of NetworkX (see example below). If an
    edge is marked as uncolored (i.e., assigned a value of ``-1`` , or not
    present in ``c``), it is painted light grey.

    Parameters
    ----------
    G : NetworkX graph
        The graph we want to visualize.

    c : dict
        A dictionary with keys representing edges and values representing
        their colors. Colors are identified by the integers $0,1,2,\\ldots$.

    palette : None or dict, optional (default=None)
        A dictionary that maps the integers $-1,0,1,\\ldots$ to RGB values.
        The in-built options are as follows

        * ``gcol.tableau`` : A collection of 21 colors provided by Tableau.
        * ``gcol.colorful`` : A collection of 57 bright colors that are
          chosen to contrast each other as much as possible.
        * ``gcol.colorblind`` : A collection of 11 colors, provided by
          Tableau, that are intended to help colorblind users.
        * If ``None``, then ``gcol.tableau`` is used.

    Returns
    -------
    dict
        list
            A sequence of RGB colors in edge order.

    Examples
    --------
    >>> import networkx as nx
    >>> import matplotlib.pyplot as plt
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.edge_coloring(G)
    >>> nx.draw_networkx(
    ...    G, pos=nx.spring_layout(G), edge_color=gcol.get_edge_colors(G, c)
    ... )
    >>> plt.show()

    Raises
    ------
    ValueError
        If ``c`` uses more colors than available in the palette.

    Notes
    -----
    User generated palettes can also be passed into this method. Descriptions
    on how to specify valid colors can be found at [1]_.

    See Also
    --------
    get_set_colors
    get_node_colors
    get_face_colors

    References
    ----------
    .. [1] Matplotlib: Specifying colors
      <https://matplotlib.org/stable/users/explain/colors/colors.html>

    """
    if palette is None:
        palette = tableau
    if len(c) == 0:
        return [palette[-1] for e in G.edges()]
    if max(c.values()) + 1 > len(palette) - 1:
        raise ValueError(
            "Error, insufficient colors are available in the chosen palette"
        )
    return [
        palette[c[e]] if e in c and c[e] >= 0
        else (0.83, 0.83, 0.83)
        for e in G.edges
    ]


def get_set_colors(G, S, S_color="yellow", other_color="grey"):
    """Generate an RGB color for each node based on if it is in ``S``.

    By default, nodes in ``S`` are painted yellow and all others are painted
    grey. This method is designed to be used with the ``node_color`` argument
    in the drawing functions of NetworkX (see example below).

    Parameters
    ----------
    G : NetworkX graph
        The graph we want to visualize.

    S : list or set
        A subset of ``G``'s nodes.

    S_color : color, optional (default='yellow')
        Desired color of the nodes in ``S``. Other options include ``'blue'``,
        ``'cyan'``, ``'green'``, ``'black'``, ``'magenta'``, ``'red'``,
        ``'white'``, and ``'yellow'``.

    other_color : color, optional (default='grey')
        Desired color of the nodes not in ``S``.

    Returns
    -------
    list
        A sequence of RGB colors, in node order

    Examples
    --------
    >>> import networkx as nx
    >>> import matplotlib.pyplot as plt
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> S = gcol.max_independent_set(G, it_limit=1000)
    >>> nx.draw_networkx(
    ...     G, pos=nx.spring_layout(G), node_color=gcol.get_set_colors(G, S)
    ... )
    >>> plt.show()

    See Also
    --------
    get_node_colors
    get_edge_colors
    get_face_colors

    Notes
    -----
    Descriptions on how to specify valid colors can be found at [1]_.

    References
    ----------
    .. [1] Matplotlib: Specifying colors
      <https://matplotlib.org/stable/users/explain/colors/colors.html>

    """
    X = set(S)
    return [S_color if u in X else other_color for u in G]


def draw_face_coloring(c, pos, external=False, palette=None):
    """
    Draw the face coloring defined by ``c`` and ``pos``

    The RGB color of each face is determined by its color label in ``c`` and
    the chosen palette. If a face is marked as uncolored (i.e., assigned a
    value of ``-1``) it is painted white.

    Parameters
    ----------
    c : dict
        A dictionary where keys represent the sequence of nodes occurring
        in each face (polygon), and values represent the face's color.
        Colors are identified by the integers $0,1,2,\\ldots$. The first
        element in ``c`` defines the external face of the embedding; the
        remaining elements define the internal faces.

    pos : dict
        A dict specifying the (x,y) coordinates of each node in the embedding.

    external : bool, optional (default=False)
        If set to ``True``, the background (corresponding to the external face
        of the embedding) is also colored, else it is left blank.

    palette : None or dict, optional (default=None)
        A dictionary that maps the integers $-1,0,1,\\ldots$ to RGB values.
        The in-built options are as follows

        * ``gcol.tableau`` : A collection of 21 colors provided by Tableau.
        * ``gcol.colorful`` : A collection of 57 bright colors that are
          chosen to contrast each other as much as possible.
        * ``gcol.colorblind`` : A collection of 11 colors, provided by
          Tableau, that are intended to help colorblind users.
        * If ``None``, then ``gcol.tableau`` is used.

    Returns
    -------
    None

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>> import matplotlib.pyplot as plt
    >>>
    >>> # Construct a small planar graph with defined node positions
    >>> G = nx.Graph()
    >>> G.add_node(0, pos=(0,0))
    >>> G.add_node(1, pos=(1,0))
    >>> G.add_node(2, pos=(0,1))
    >>> G.add_node(3, pos=(1,1))
    >>> G.add_edges_from([(0,1),(0,2),(0,3),(1,3),(2,3)])
    >>>
    >>> # Color the faces of the embedding and draw to the screen
    >>> pos = nx.get_node_attributes(G, "pos")
    >>> c = face_coloring(G, pos)
    >>> draw_face_coloring(c, pos)
    >>> plt.show()

    Raises
    ------
    ValueError
        If ``c`` uses more colors than available in the palette.

    Notes
    -----
    User generated palettes can also be passed into this method. In such cases
    it is good practice to map the value ``-1`` to the color white.
    Descriptions on how to specify valid colors can be found at [1]_.

    See Also
    --------
    get_set_colors
    get_edge_colors
    get_node_colors

    References
    ----------
    .. [1] Matplotlib: Specifying colors
      <https://matplotlib.org/stable/users/explain/colors/colors.html>

    """
    if palette is None:
        palette = tableau
    if len(c) == 0:
        return []
    if max(c.values()) + 1 > len(palette) - 1:
        raise ValueError(
            "Error, insufficient colors are available in the chosen palette"
        )
    fig, ax = plt.subplots()
    ax.autoscale()
    faceList = list(c.keys())
    if external:
        ax.set_facecolor(palette[c[faceList[0]]])
    for i in range(1, len(faceList)):
        coords = [[pos[u][0], pos[u][1]] for u in faceList[i]]
        p = Polygon(coords, facecolor=(palette[c[faceList[i]]]))
        ax.add_patch(p)


def kempe_chain(G, c, s, j):
    """Return the set of nodes in a Kempe chain.

    Given a node coloring ``c`` of a graph ``G``, this method returns the set
    of nodes in the Kempe chain generated from a source node ``s`` using the
    color ``j``.

    A Kempe chain is a connected set of nodes in a graph that alternates
    between two colors [1]_. Equivalently, it is a maximal connected subgraph
    that contains nodes of at most two colors. Interchanging the colors of
    the nodes in a Kempe chain creates a new coloring that uses the same
    number of colors or one fewer color. Two $k$-colorings of a graph are
    considered *Kempe equivalent* if one can be obtained from the other
    through a series of Kempe chain interchanges [2]_. It is also known that,
    if $k$ is larger than the degeneracy of a graph, then all $k$-colorings
    of this graph are Kempe equivalent [2]_.

    Parameters
    ----------
    G : NetworkX graph
        The graph that we want to compute a Kempe chain for.

    c : dict
        A node coloring of ``G``. Pairs of adjacent nodes cannot be allocated
        to the same color. Any uncolored nodes ``u`` should have ``c[u]==-1``.

    s : node
        The source node that we will generate the Kempe chain from.

    j : int
        The second color to use. The first color is that of ``s``.

    Returns
    -------
    set
        The set of nodes, reachable from ``s``, that alternate between colors
        ``i`` and ``j`` (where ``c[s]==i``).

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.node_coloring(G)
    >>> S = gcol.kempe_chain(G, c, 0, 1)
    >>> print("Example Kempe chain =", S)
    Example Kempe chain = {0, 1, 2, 4, 6, 8, 10, 17, 18, 19}

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

    ValueError
        If ``c`` contains a pair of adjacent nodes assigned to the same color.

        If ``c`` contains an invalid color label or no color label for ``s``.

        If ``G`` contains a node that is not in ``c``.

    Notes
    -----
    This method uses an extension of breadth-first search and operates in
    $O(n+m)$ time. If ``c[s]==j``, then the Kempe chain contains node ``s``
    only.

    See Also
    --------
    equitable_node_k_coloring

    References
    ----------
    .. [1] Wikipedia: Kempe Chain
      <https://en.wikipedia.org/wiki/Kempe_chain>
    .. [2] Cranston, D. (2024) Graph Coloring Methods
      <https://graphcoloringmethods.com/>

    """
    if G.is_directed() or G.is_multigraph() or nx.number_of_selfloops(G) > 0:
        raise NotImplementedError(
            "Error, this method cannot be used with directed graphs,",
            "multigraphs, or graphs with self-loops"
        )
    for u in G:
        for v in G[u]:
            if c[u] != -1 and c[v] != -1 and c[u] == c[v]:
                raise ValueError(
                    "Error, the graph cannot contain adjacent nodes of the ",
                    "same color. Also, uncolored nodes v must have c[v] == -1"
                )
    if s not in c or c[s] < 0:
        raise ValueError(
            "Error, node s must be present in the graph and assigned a color"
        )
    i = c[s]
    if i == j:
        return {s}
    # If we are here, use bredth-first search to identify the Kempe chain
    status = {s: 1}
    Q = deque([s])
    Chain = set()
    while Q:
        u = Q[0]
        for v in G[u]:
            if (c[u] == j and c[v] == i) or (c[u] == i and c[v] == j):
                if v not in status:
                    status[v] = 1
                    Q.append(v)
        Q.popleft()
        status[u] = 2
        Chain.add(u)
    return Chain


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
    c = nc._dsatur(G)
    for v in c:
        if c[v] > 0:
            c[v] = -1
    cost, c, its = nc._partialcol(G, 1, c, W, it_limit, verbose)
    return [v for v in c if c[v] == 0]


def min_cost_k_coloring(G, k, weight=None, weights_at="nodes", it_limit=0,
                        verbose=0):
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
    c = nc._dsatur(G)
    if weights_at == "nodes":
        W = _getNodeWeights(G, weight)
        for v in c:
            if c[v] >= k:
                c[v] = -1
        cost, c, its = nc._partialcol(G, k, c, W, it_limit, verbose)
    else:
        W = _getEdgeWeights(G, weight)
        for v in c:
            if c[v] >= k:
                c[v] = random.randint(0, k - 1)
        cost, c, its = nc._tabucol(G, k, c, W, it_limit, verbose)
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
        * ``None`` : No optimization is performed.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Only applicable
        when using ``opt_alg=2`` or ``opt_alg=3``.

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
    equitable_edge_k_coloring
    kempe_chain

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
    c = enc._dsatur_equitable(G, k, W)
    if c is None:
        if opt_alg is None:
            raise ValueError(
                "Error, a k-coloring could not be found. Try changing the "
                "optimisation options or increasing k"
            )
        c = nc._dsatur(G)
        if opt_alg == 2:
            WPrime = _getEdgeWeights(G, None)
        else:
            WPrime = _getNodeWeights(G, None)
        c = nc._reducecolors(G, c, k, WPrime, opt_alg, it_limit, verbose)
        if max(c.values()) + 1 > k:
            raise ValueError(
                "Error, could not construct a k-coloring of this graph. Try "
                "increasing k or using more optimisation"
            )
    # If we are here we have a k-coloring. Attempt to decrease the SD
    # across the color classes using a steepest descent heuristic
    return enc._LS_equitable(G, c, k, W, verbose)


def node_k_coloring(G, k, opt_alg=None, it_limit=0, verbose=0):
    """Attempt to color the nodes of a graph using ``k`` colors.

    This is done so that adjacent nodes have different colors. A set of nodes
    assigned to the same color corresponds to an independent set; hence the
    equivalent aim is to partition the graph's nodes into ``k`` independent
    sets.

    Determining whether a node $k$-coloring exists for $G$ is NP-complete.
    This method therefore includes options for using an exact exponential-time
    algorithm (based on backtracking), or a choice of two polynomial-time
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
        * None : No optimization is performed.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Only applicable
        when using ``opt_alg=2`` or ``opt_alg=3``.

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
    edge_k_coloring

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
    c = enc._dsatur_equitable(G, k, W)
    if c is None:
        if opt_alg is None:
            raise ValueError(
                "Error, a k-coloring could not be found. Try changing the "
                "optimisation options or increasing k"
            )
        c = nc._dsatur(G)
        if opt_alg == 2:
            W = _getEdgeWeights(G, None)
        c = nc._reducecolors(G, c, k, W, opt_alg, it_limit, verbose)
        if max(c.values()) + 1 > k:
            raise ValueError(
                "Error, could not construct a k-coloring of this graph. Try "
                "increasing k or using more optimisation"
            )
    # If we are here we have a k-coloring
    return c


def equitable_edge_k_coloring(G, k, weight=None, opt_alg=None, it_limit=0,
                              verbose=0):
    """Attempt to color the edges of a graph using ``k`` colors.

    This is done so that (a) adjacent edges have different colors, and (b) the
    weight of each color class is equal. (A pair of edges is considered
    adjacent if and only if they share a common endpoint.) If ``weight=None``,
    the weight of a color class is the number of edges assigned to that color;
    otherwise, it is the sum of the weights of the edges assigned to that
    color.

    Equivalently, this routine seeks to partition the graph's edges into $k$
    matchings so that the weight of each matching is equal.

    This method first follows the steps used by the :meth:`edge_k_coloring`
    method to try and find an edge $k$-coloring. That is, edge colorings of a
    graph $G$ are determined by forming $G$'s line graph $L(G)$ and then
    passing $L(G)$ to the :meth:`node_k_coloring` method. All parameters are
    therefore the same as the latter. (Note that, if a graph $G=(V,E)$ has $n$
    nodes and $m$ edges, its line graph $L(G)$ will have $m$ nodes and
    $\\frac{1}{2}\\sum_{v\\in V}\\deg(v)^2 - m$ edges.)

    If an edge $k$-coloring cannot be determined by the algorithm, a
    ``ValueError`` exception is raised. Otherwise, once an edge $k$-coloring
    has been formed, the algorithm uses a bespoke local search operator to
    reduce the standard deviation in weights across the $k$ colors.
    In solutions returned by this method, adjacent edges always receive
    different colors; however, the coloring is not guaranteed to be equitable,
    even if an equitable edge $k$-coloring exists.

    Parameters
    ----------
    G : NetworkX graph
        The edges of this graph will be colored.

    k : int
        The number of colors to use.

    weight : None or string, optional (default=None)
        If ``None``, every edge is assumed to have a weight of ``1``. If a
        string, this should correspond to a defined edge attribute. Edge
        weights must be positive.

    opt_alg : None or int, optional (default=None)
        An integer specifying the optimization method that will be used to try
        to reduce the number of colors (if this is seen to be greater than
        ``k``). It must be one of the following

        * ``1`` : An exact, exponential-time algorithm based on backtracking.
          The algorithm halts only when the existence of an edge $k$-coloring
          has been proved or disproved.
        * ``2`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing adjacent nodes in $L(G)$ to have the
          same color. Each iteration has a complexity $O(m + kn)$, where $n$
          is the number of nodes in $L(G)$, $m$ is the number of edges in
          $L(G)$, and $k$ is the number of colors in the current solution.
        * ``3`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes in $L(G)$ to be uncolored.
          Each iteration has a complexity $O(m + kn)$, as above.
        * None : No optimization is performed.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Only applicable
        when using ``opt_alg=2`` or ``opt_alg=3``.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process. The higher the value, the more information.

    Returns
    -------
    dict
        A dictionary with keys representing edges and values representing
        their colors. Colors are identified by the integers
        $0,1,2,\\ldots,k-1$.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.equitable_edge_k_coloring(G, 4)
    >>> P = gcol.partition(c)
    >>> print(P)
    [[(11, 12), (18, 19), (16, 17), (9, 10), ..., (5, 6)]]
    >>> print("Size of smallest color class =", min(len(j) for j in P))
    Size of smallest color class = 7
    >>> print("Size of biggest color class =", max(len(j) for j in P))
    Size of biggest color class = 8
    >>>
    >>> #Now add some (arbitrary) weights to the edges
    >>> for e in G.edges():
    >>>     G.add_edge(e[0], e[1], weight = abs(e[0]-e[1]))
    >>> c = gcol.equitable_edge_k_coloring(G, 5, weight="weight")
    >>> P = gcol.partition(c)
    >>> print(P)
    [[(11, 12), (18, 19), (4, 17), (13, 14), ..., (2, 6)]]
    >>> print(
    ...     "Weight of lightest color class =",
    ...     min(sum(G[u][v]["weight"] for u, v in j) for j in P)
    ... )
    Weight of lightest color class = 23
    >>> print(
    ...     "Weight of heaviest color class =",
    ...     max(sum(G[u][v]["weight"] for u, v in j) for j in P)
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

        If a clique larger than ``k`` is observed in the line graph of $G$.

        If ``k`` is less than the maximum degree in ``G``.

        If an edge $k$-coloring could not be determined.

        If an edge with a non-positive weight is specified.

    KeyError
        If an edge does not have the attribute defined by ``weight``

    Notes
    -----
    As mentioned, in this implementation edge colorings of a graph $G$ are
    determined by forming $G$'s line graph $L(G)$ and then following the same
    steps as the :meth:`node_k_coloring` method to try and find a node
    $k$-coloring of $L(G)$; however, it also takes edge weights into account
    if needed. If an edge $k$-coloring is achieved, a bespoke local search
    operator (based on steepest descent) is then used to try to reduce the
    standard deviation in weights across the $k$ color classes. This follows
    the same steps as the :meth:`equitable_node_k_coloring` method, using
    $L(G)$. Further details on this optimization method can be found in Chapter
    7 of [2]_, or in [3]_.

    All the above algorithms are described in detail in [2]_. The c++ code used
    in [2]_ and [4]_ forms the basis of this library's Python implementations.

    See Also
    --------
    edge_k_coloring
    node_k_coloring
    equitable_node_k_coloring
    kempe_chain

    References
    ----------
    .. [1] Wikipedia: Vizing's Theorem
      <https://en.wikipedia.org/wiki/Vizing%27s_theorem>
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
    if len(G) == 0 or G.number_of_edges() == 0:
        return {}
    maxdeg = max(d for v, d in G.degree())
    if k < maxdeg:
        raise ValueError(
            "Error, a k-coloring of this graph does not exist. "
            "Try increasing k"
        )
    H = nx.line_graph(G)
    H.add_nodes_from((v, G.edges[v]) for v in H)
    return equitable_node_k_coloring(
        H, k, weight=weight, opt_alg=opt_alg, it_limit=it_limit,
        verbose=verbose
    )


def edge_k_coloring(G, k, opt_alg=None, it_limit=0, verbose=0):
    """Attempt to color the edges of a graph ``G`` using ``k`` colors.

    This is done so that adjacent edges have different colors (a pair of edges
    is considered adjacent if and only if they share a common endpoint). A set
    of edges assigned to the same color corresponds to a matching; hence the
    equivalent aim is to partition the graph's edges into ``k`` matchings.

    The smallest number of colors needed for coloring the edges of a graph $G$
    is known as the graph's chromatic index, denoted by $\\chi'(G)$.
    Equivalently, $\\chi'(G)$ is the minimum number of matchings needed to
    partition the nodes of a simple graph $G$. According to Vizing's theorem
    [1]_, $\\chi'(G)$ is either $\\Delta(G)$ or $\\Delta(G) + 1$, where
    $\\Delta(G)$ is the maximum degree in $G$. The problem of determining an
    edge $k$-coloring is polynomially solvable for any $k > \\Delta(G)$.
    Similarly, it is certain no edge $k$-coloring exists for $k < \\Delta(G)$.
    For $k = \\Delta(G)$, however, the problem is NP-hard.

    This method therefore includes options for using an exact exponential-time
    algorithm (based on backtracking), or a choice of two polynomial-time
    heuristic algorithms (based on local search). The exact algorithm is
    generally only suitable for larger values of $k$, for graphs that are
    small, or graphs that have topologies suited to its search strategies.
    In all other cases, the local search algorithms are more appropriate.

    This method follows the steps used by the :meth:`node_k_coloring` method.
    That is, edge $k$-colorings of a graph $G$ are determined by forming $G$'s
    line graph $L(G)$ and then passing $L(G)$ to the :meth:`node_k_coloring`
    method. All parameters are therefore the same as the latter. (Note that,
    if a graph $G=(V,E)$ has $n$ nodes and $m$ edges, its line graph $L(G)$
    will have $m$ nodes and $\\frac{1}{2}\\sum_{v\\in V}\\deg(v)^2 - m$ edges.)

    If an edge $k$-coloring cannot be determined by the algorithm, a
    ``ValueError`` exception is raised. Otherwise, an edge $k$-coloring is
    returned.

    Parameters
    ----------
    G : NetworkX graph
        The edges of this graph will be colored.

    k : int
        The number of colors to use.

    opt_alg : None or int, optional (default=None)
        An integer specifying the optimization method that will be used to try
        to reduce the number of colors (if this is seen to be greater than
        $k$). It must be one of the following

        * ``1`` : An exact, exponential-time algorithm based on backtracking.
          The algorithm halts only when the existence of an edge $k$-coloring
          has been proved or disproved.
        * ``2`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing adjacent nodes in $L(G)$ to have the
          same color. Each iteration has a complexity $O(m + kn)$, where $n$
          is the number of nodes in $L(G)$, $m$ is the number of edges in
          $L(G)$, and $k$ is the number of colors in the current solution.
        * ``3`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes in $L(G)$ to be uncolored. Each
          iteration has a complexity $O(m + kn)$, as above.
        * ``None`` : No optimization is performed.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Only applicable
        when using ``opt_alg=2`` or ``opt_alg=3``.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process. The higher the value, the more information.

    Returns
    -------
    dict
        A dictionary with keys representing edges and values representing
        their colors. Colors are identified by the integers
        $0,1,2,\\ldots,k-1$.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.edge_k_coloring(G, 4)
    >>> print(c)
    {(11, 12): 0, (11, 18): 1, (10, 11): 2, ..., (6, 7): 2}
    >>>
    >>> c = gcol.edge_k_coloring(G, 3)
    >>> print(c)
    {(11, 12): 0, (11, 18): 1, (10, 11): 2, ..., (7, 8): 0}

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

        If a clique larger than ``k`` is observed in the line graph of $G$.

        If ``k`` is less than the maximum degree in ``G``.

        If an edge $k$-coloring could not be determined.

    Notes
    -----
    As mentioned, in this implementation, edge colorings of a graph $G$ are
    determined by forming $G$'s line graph $L(G)$ and then passing $L(G)$ to
    the :meth:`node_k_coloring` method. All details are therefore the same as
    those in the latter. The routine halts immediately once an edge
    $k$-coloring has been achieved.

    All the above algorithms and bounds are described in detail in [2]_. The
    c++ code used in [2]_ and [3]_ forms the basis of this library's Python
    implementations.

    See Also
    --------
    edge_coloring
    equitable_edge_k_coloring
    node_k_coloring

    References
    ----------
    .. [1] Wikipedia: Vizing's Theorem
      <https://en.wikipedia.org/wiki/Vizing%27s_theorem>
    .. [2] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
      Applications (second ed.). Springer. ISBN: 978-3-030-81053-5.
      <https://link.springer.com/book/10.1007/978-3-030-81054-2>.
    .. [3] Lewis, R: Graph Colouring Algorithm User Guide
      <https://rhydlewis.eu/gcol/>

    """
    if k < 0:
        raise ValueError("Error, positive integer needed for k")
    _check_params(G, "dsatur", opt_alg, it_limit, verbose)
    if len(G) == 0 or G.number_of_edges() == 0:
        return {}
    maxdeg = max(d for v, d in G.degree())
    if k < maxdeg:
        raise ValueError(
            "Error, a k-coloring of this graph does not exist. "
            "Try increasing k"
        )
    H = nx.line_graph(G)
    return node_k_coloring(H, k, opt_alg=opt_alg, it_limit=it_limit,
                           verbose=verbose)


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
    exponential-time algorithm (based on backtracking), or a choice of two
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
        * 3 : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes to be uncolored. Each iteration
          has a complexity $O(m + kn)$, as above.
        * None : No optimization is performed.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Only applicable
        when using ``opt_alg=2`` or ``opt_alg=3``.

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

    If local search is used (``opt_alg=2`` or ``opt_alg=3``), the algorithm
    removes a color class and uses the chosen local search routine to seek a
    proper coloring using the remaining colors. If this is successful, the
    process repeats. The algorithm is executed until a solution using $|C|$
    colors has been identified (as above), or until the iteration limit is
    reached. Fewer colors (but longer run times) occur with larger iteration
    limits.

    If ``opt_alg=2``, the TabuCol algorithm is used. This algorithm is based
    on tabu search and operates by fixing the number of colors but allowing
    clashes to occur (a clash is the occurrence of two adjacent nodes having
    the same color). The aim is to alter the color assignments so that the
    number of clashes is reduced to zero. Each iteration of TabuCol has
    complexity $O(nk + m)$, where $k$ is the number of colors currently being
    used. The process also uses $O(nk + m)$ memory.

    If ``opt_alg=3``, the PartialCol algorithm is used. This algorithm is also
    based on tabu search and operates by fixing the number of colors but
    allowing some nodes to be left uncolored. The aim is to make alterations
    to the color assignments so that no uncolored nodes remain. As with
    TabuCol, each iteration of PartialCol has complexity $O(nk +m)$ and uses
    $O(nk + m)$ memory.

    As stated above, if ``verbose`` is set to a positive integer, output is
    produced during the execution of the chosen optimzation algorithm. If the
    backtracking algorithm is being used, the stated iterations refer to the
    number of calls to its recursive function. Otherwise, iterations refer to
    the $O(nk +m)$ processes mentioned above. If no optimization is performed,
    no output is produced.

    All the above algorithms and bounds are described in detail in [4]_. The
    c++ code used in [4]_ and [5]_ forms the basis of this library's Python
    implementations.

    See Also
    --------
    chromatic_number
    node_k_coloring
    edge_coloring

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
    elif G.number_of_edges() == 0:
        return {u: 0 for u in G}
    # Make an initial coloring based on the chosen strategy
    if strategy == "random":
        V = list(G)
        random.shuffle(V)
        c = nc._greedy(G, V)
    elif strategy == "welsh_powell":
        V = sorted(G, key=G.degree, reverse=True)
        c = nc._greedy(G, V)
    elif strategy == "rlf":
        c = nc._rlf(G)
    else:
        c = nc._dsatur(G)
    # If selected, employ the chosen optimisation method
    if opt_alg is None:
        return c
    if opt_alg == 2:
        W = _getEdgeWeights(G, None)
    else:
        W = _getNodeWeights(G, None)
    cliqueNum = nx.approximation.large_clique_size(G)
    return nc._reducecolors(G, c, cliqueNum, W, opt_alg, it_limit, verbose)


def edge_coloring(G, strategy="dsatur", opt_alg=None, it_limit=0, verbose=0):
    """Return a coloring of a graph's edges.

    An edge coloring of a graph is an assignment of colors to edges so that
    adjacent edges have different colors (a pair of edges is considered
    adjacent if and only if they share a common endpoint). The aim is to use
    as few colors as possible. A set of edges assigned to the same color
    corresponds to a matching; hence the equivalent aim is to partition the
    graph's edges into a minimum number of matchings.

    The smallest number of colors needed for coloring the edges of a graph $G$
    is known as the graph's chromatic index, denoted by $\\chi'(G)$.
    Equivalently, $\\chi'(G)$ is the minimum number of matchings needed to
    partition the nodes of a simple graph $G$. According to Vizing's theorem
    [1]_, $\\chi'(G)$ is either $\\Delta(G)$ or $\\Delta(G) + 1$, where
    $\\Delta(G)$ is the maximum degree in $G$.

    Determining an edge coloring that minimizes the number of colors is an
    NP-hard problem. This method therefore includes options for using an
    exponential-time exact algorithm (based on backtracking), or a choice of
    two polynomial-time heuristic algorithms (based on local search). The
    exact algorithm is generally only suitable for graphs that are small,
    or that have topologies suited to its search strategies. In all other
    cases, the local search algorithms are more appropriate.

    In this implementation, edge colorings of a graph $G$ are determined by
    forming $G$'s line graph $L(G)$, and then passing $L(G)$ to the
    :meth:`node_coloring` method. All parameters are therefore the same as the
    latter. (Note that, if a graph $G=(V,E)$ has $n$ nodes and $m$ edges, its
    line graph $L(G)$ will have $m$ nodes and $\\frac{1}{2}\\sum_{v\\in V}
    \\deg(v)^2 - m$ edges.)

    Parameters
    ----------
    G : NetworkX graph
        The edges of this graph will be colored.

    strategy : string, optional (default='dsatur')
        A string specifying the method used to generate the initial solution.
        It must be one of the following:

        * ``'random'`` : Randomly orders $L(G)$'s nodes and then applies the
          greedy algorithm for graph node coloring [2]_.
        * ``'welsh-powell'`` : Orders $L(G)$'s nodes by decreasing degree,
          then applies the greedy algorithm.
        * ``'dsatur'`` : Uses the DSatur algorithm for graph node coloring
          on $L(G)$ [3]_.
        * ``'rlf'`` : Uses the recursive largest first (RLF) algorithm for
          graph node coloring on $L(G)$ [4]_.

    opt_alg : None or int, optional (default=None)
        An integer specifying the optimization method that will be used to try
        to reduce the number of colors. It must be one of the following

        * ``1`` : An exact, exponential-time algorithm based on backtracking.
          The algorithm halts only when an optimal solution has been found.
        * ``2`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing adjacent nodes in $L(G)$ to have the
          same color. Each iteration has a complexity $O(m + kn)$, where $n$
          is the number of nodes in $L(G)$, $m$ is the number of edges in
          $L(G)$, and $k$ is the number of colors in the current solution.
        * ``3`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes in $L(G)$ to be uncolored. Each
          iteration has a complexity $O(m + kn)$, as above.
        * ``None`` : No optimization is performed.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Only applicable
        when using ``opt_alg=2`` or ``opt_alg=3``.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process. The higher the value, the more information.

    Returns
    -------
    dict
        A dictionary with keys representing edges and values representing their
        colors. Colors are identified by the integers $0,1,2,\\ldots$. The
        number of colors being used in a solution ``c`` is therefore
        ``max(c.values()) + 1``.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> c = gcol.edge_coloring(G)
    >>> print("Coloring is", c)
    Coloring is {(11, 12): 0, (11, 18): 1, ..., (7, 8): 0}
    >>>
    >>> print("Number of colors =", max(c.values()) + 1)
    Number of colors = 3
    >>>
    >>> c = gcol.edge_coloring(G, strategy="rlf", opt_alg=2, it_limit=1000)
    >>> print("Coloring is", c)
    Coloring is {(3, 4): 0, (17, 18): 0, ..., (7, 14): 2}
    >>>
    >>> print("Number of colors =", max(c.values()) + 1)
    Number of colors = 3

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
    As mentioned, in this implementation, edge colorings of a graph $G$ are
    determined by forming $G$'s line graph $L(G)$ and then passing $L(G)$ to
    the :meth:`node_coloring` method. All details are therefore the same as
    those in the latter, where they are documented more fully.

    All the above algorithms and bounds are described in detail in [5]_. The
    c++ code used in [5]_ and [6]_ forms the basis of this library's Python
    implementations.

    See Also
    --------
    node_coloring
    chromatic_index
    edge_k_coloring

    References
    ----------
    .. [1] Wikipedia: Vizing's Theorem
      <https://en.wikipedia.org/wiki/Vizing%27s_theorem>
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
    if len(G) == 0 or G.number_of_edges() == 0:
        return {}
    # Now simply color the nodes of the line graph H of G
    maxdeg = max(d for v, d in G.degree())
    H = nx.line_graph(G)
    if strategy == "random":
        V = list(H)
        random.shuffle(V)
        c = nc._greedy(H, V)
    elif strategy == "welsh_powell":
        V = sorted(H, key=H.degree, reverse=True)
        c = nc._greedy(H, V)
    elif strategy == "rlf":
        c = nc._rlf(H)
    else:
        c = nc._dsatur(H)
    # If selected, employ the chosen optimisation method
    if opt_alg is None:
        return c
    if opt_alg == 2:
        W = _getEdgeWeights(H, None)
    else:
        W = _getNodeWeights(H, None)
    cliqueNum = nx.approximation.large_clique_size(H)
    return nc._reducecolors(H, c, max(cliqueNum, maxdeg), W, opt_alg, it_limit,
                            verbose)


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
    chromatic_index
    node_coloring

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
    c = nc._backtrackcol(G, cliqueNum, 0)
    return max(c.values()) + 1


def chromatic_index(G):
    """Return the chromatic index of the graph ``G``.

    The chromatic index of a graph $G$ is the minimum number of colors needed
    to color the edges so that no two adjacent edges have the same color (a
    pair of edges is considered adjacent if and only if they share a common
    endpoint). The chromatic index is commonly denoted by $\\chi'(G)$.
    Equivalently, $\\chi'(G)$ is the minimum number of matchings needed to
    partition the edges of $G$. According to Vizing's theorem [1]_, $\\chi'(G)$
    is equal to either $\\Delta(G)$ or $\\Delta(G) + 1$, where $\\Delta(G)$ is
    the maximum degree in $G$.

    Determining the chromatic index of a graph is NP-hard. The approach used
    here is based on the backtracking algorithm of [2]_. This is exact but
    operates in exponential time. It is therefore only suitable for graphs
    that are small, or that have topologies suited to its search strategies.

    In this implementation, edge colorings of a graph $G$ are determined by
    forming $G$'s line graph $L(G)$ and then passing $L(G)$ to the
    :meth:`chromatic_number` method.

    Parameters
    ----------
    G : NetworkX graph
        The chromatic index for this graph will be calculated.

    Returns
    -------
    int
        A nonnegative integer that gives the chromatic index of ``G``.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> chi = gcol.chromatic_index(G)
    >>> print("Chromatic index is", chi)
    Chromatic index is 3

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

    Notes
    -----
    The backtracking approach used here is an implementation of the exact
    algorithm described in [2]_. It has exponential runtime and halts only when
    the chromatic index has been determined. Further details of this algorithm
    are given in the notes section of the :meth:`node_coloring` method.

    The above algorithm is described in detail in [2]_. The c++ code used in
    [2]_ and [3]_ forms the basis of this library's Python implementations.

    See Also
    --------
    chromatic_number
    node_coloring

    References
    ----------
    .. [1] Wikipedia: Vizing's Theorem
      <https://en.wikipedia.org/wiki/Vizing%27s_theorem>
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
    if len(G) == 0 or G.number_of_edges() == 0:
        return 0
    maxdeg = max(d for v, d in G.degree())
    H = nx.line_graph(G)
    cliqueNum = nx.approximation.large_clique_size(H)
    c = nc._backtrackcol(H, max(cliqueNum, maxdeg), 0)
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
    backtracking), or a choice of two polynomial-time heuristic algorithms
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
        * ``None`` : No optimization is performed.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Only applicable
        when using ``opt_alg=2`` or ``opt_alg=3``.

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
    edge_precoloring

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


def edge_precoloring(
    G, precol=None, strategy="dsatur", opt_alg=None, it_limit=0, verbose=0
):
    """Return a coloring of a graph's edges where some edges are precolored.

    An edge coloring of a graph is an assignment of colors to edges so that
    adjacent edges have different colors (a pair of edges is considered
    adjacent if and only if they share a common endpoint). The aim is to use
    as few colors as possible. A set of edges assigned to the same color
    corresponds to a matching; hence the equivalent aim is to partition the
    graph's edges into a minimum number of matchings.

    In the edge precoloring problem, some of the edges have already been
    assigned colors. The aim is to allocate colors to the remaining edges so
    that we get a full edge coloring that uses a minimum number of colors.

    The edge precoloring problem is NP-hard. This method therefore includes
    options for using an exponential-time exact algorithm (based on
    backtracking), or a choice of two polynomial-time heuristic algorithms
    (based on local search). The exact algorithm is generally only suitable
    for graphs that are small, or that have topologies suited to its search
    strategies. In all other cases, the local search algorithms are more
    appropriate.

    In this implementation, edge colorings of a graph $G$ are determined by
    forming $G$'s line graph $L(G)$ and then passing $L(G)$ to the
    :meth:`node_precoloring` method. All parameters are therefore the same as
    the latter. (Note that, if a graph $G=(V,E)$ has $n$ nodes and $m$ edges,
    its line graph $L(G)$ will have $m$ nodes and $\\frac{1}{2}\\sum_{v\\in V}
    \\deg(v)^2 - m$ edges.)

    Parameters
    ----------
    G : NetworkX graph
        The edges of this graph will be colored.

    precol : None or dict, optional (default=None)
        A dictionary that specifies the colors of any precolored edges.

    strategy : string, optional (default='dsatur')
        A string specifying the method used to generate the initial solution.
        It must be one of the following:

        * ``'random'`` : Randomly orders $L(G)$'s nodes and then applies the
          greedy algorithm for graph node coloring [1]_.
        * ``'welsh-powell'`` : Orders $L(G)$'s nodes by decreasing degree,
          then applies the greedy algorithm.
        * ``'dsatur'`` : Uses the DSatur algorithm for graph node coloring on
          $L(G)$ [2]_.
        * ``'rlf'`` : Uses the recursive largest first (RLF) algorithm for
          graph node coloring on $L(G)$ [3]_.

    opt_alg : None or int, optional (default=None)
        An integer specifying the optimization method that will be used to try
        to reduce the number of colors. It must be one of the following

        * ``1`` : An exact, exponential-time algorithm based on backtracking.
          The algorithm halts only when an optimal solution has been found.
        * ``2`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing adjacent nodes in $L(G)$ to have the
          same color. Each iteration has a complexity $O(m + kn)$, where $n$ is
          the number of nodes in $L(G)$, $m$ is the number of edges, and $k$ is
          the number of colors in the current solution.
        * ``3`` : A local search algorithm that seeks to reduce the number of
          colors by temporarily allowing nodes in $L(G)$ to be uncolored. Each
          iteration has a complexity $O(m + kn)$, as above.
        * ``None`` : No optimization is performed.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Only applicable
        when using ``opt_alg=2`` or ``opt_alg=3``.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process. The higher the value, the more information.

    Returns
    -------
    dict
        A dictionary with keys representing edges and values representing their
        colors. Colors are identified by the integers $0,1,2,\\ldots$. The
        number of colors being used in a solution ``c`` is therefore
        ``max(c.values()) + 1``. If ``precol[(u,v)]==j`` then ``c[(u,v)]==j``.

    Examples
    --------
    >>> import networkx as nx
    >>> import gcol
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> p = {(0, 1):0, (8, 9): 1, (10, 11): 2, (11, 12): 3}
    >>> c = gcol.edge_precoloring(G, precol=p)
    >>> print("Coloring is",c)
    Coloring is {(0, 1): 0, (8, 9): 1, ..., (5, 6): 2}
    >>>
    >>> print("Number of colors =", max(c.values()) + 1)
    Number of colors = 4

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

        If ``precol`` contains an edge that is not in ``G``.

        If ``precol`` contains a non-integer color label.

        If ``precol`` contains a pair of adjacent edges assigned to the same
        color.

        If ``precol`` uses an integer color label $j$, but there exists a color
        label $0 \\leq i < j$ that is not being used.

    Notes
    -----
    As mentioned, in this implementation, edge colorings of a graph $G$ are
    determined by forming $G$'s line graph $L(G)$ and then passing $L(G)$ to
    the :meth:`node_precoloring` method. All details are therefore the same as
    those in the latter, where they are documented.

    All the above algorithms and bounds are described in detail in [4]_. The
    c++ code used in [4]_ and [5]_ forms the basis of this library's Python
    implementations.

    See Also
    --------
    edge_coloring
    node_precoloring
    node_coloring

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
    if len(G) == 0 or G.number_of_edges() == 0:
        return {}
    if precol is None or precol == {}:
        return edge_coloring(
            G, strategy=strategy, opt_alg=opt_alg, it_limit=it_limit,
            verbose=verbose
        )
    if not isinstance(precol, dict):
        raise TypeError(
            "Error, the precoloring should be a dict that assigns a subset of "
            "the graph's edges to colors"
        )
    cols = set()
    for u, v in precol:
        if not G.has_edge(u, v):
            raise ValueError(
                "Error, an edge is defined in the precoloring that is not in "
                "the graph"
            )
        if not isinstance(precol[u, v], int):
            raise ValueError(
                "Error, all color labels in the precoloring should be integers"
            )
        cols.add(precol[u, v])
    for e1 in precol:
        for e2 in precol:
            if e1 != e2:
                if (
                    e1[0] == e2[0]
                    or e1[0] == e2[1]
                    or e1[1] == e2[0]
                    or e1[1] == e2[1]
                ):
                    if precol[e1] == precol[e2]:
                        raise ValueError(
                            "Error, there are adjacent edges in the "
                            "precoloring with the same color"
                        )
    k = max(precol.values()) + 1
    for i in range(k):
        if i not in cols:
            raise ValueError(
                "Error, the color labels in the precoloring should be in "
                "{0,1,2,...} and each color should be being used by at least "
                "one edge"
            )
    H = nx.line_graph(G)
    return node_precoloring(
        H, precol=precol, strategy=strategy, opt_alg=opt_alg,
        it_limit=it_limit, verbose=verbose
    )


def face_coloring(G, pos, strategy="dsatur", opt_alg=None, it_limit=0,
                  verbose=0):
    """Return a coloring of a planar graph's faces.

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
        The faces of this graph will be colored.

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
        * ``None`` : No optimization is performed.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Only applicable
        when using ``opt_alg=2`` or ``opt_alg=3``.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process. The higher the value, the more information.

    Returns
    -------
    dict
        A dictionary with keys representing faces and values representing their
        colors. Colors are identified by the integers $0,1,2,\\ldots$. The
        number of colors being used in a solution ``c`` is therefore
        ``max(c.values()) + 1``. Each face (key) is a tuple that gives the
        sequence of nodes that surround it. These correspond to cycles in
        ``G``. The first element in ``c`` defines the external face; the
        remainder defines the internal faces. For internal faces, the nodes
        are listed in a counterclockwise order; for the external face, the
        nodes are listed in a clockwise order.

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
    node_coloring
    edge_coloring
    face_chromatic_number

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
    if len(G) == 0 or G.number_of_edges() == 0:
        return {}
    # Color the nodes of the dual graph H of the emedding defined by G and pos
    H, faces = fc._get_dual(G, pos)
    c = node_coloring(H, strategy=strategy, opt_alg=opt_alg,
                      it_limit=it_limit, verbose=verbose)
    # Return the face coloring of G.
    return {tuple(faces[i]): c[i] for i in range(len(H))}


def face_chromatic_number(G):
    """Return the face chromatic number of the planar graph ``G``.

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
        The face chromatic number for this graph will be calculated.

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
    chromatic_number
    face_coloring

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
    if nx.has_bridges(G):
        raise ValueError("Supplied graph is not bridge-free")
    if len(G) == 0 or G.number_of_edges() == 0:
        return 0
    H, faces = fc._get_dual(G, nx.planar_layout(G))
    cliqueNum = nx.approximation.large_clique_size(H)
    c = nc._backtrackcol(H, cliqueNum, 0)
    return max(c.values()) + 1


def face_k_coloring(G, pos, k, opt_alg=None, it_limit=0, verbose=0):
    """Attempt to color the faces of a planar graph ``G`` using ``k`` colors.

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
        The faces of this graph will be colored.

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
        * ``None`` : No optimization is performed.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Only applicable
        when using ``opt_alg=2`` or ``opt_alg=3``.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process. The higher the value, the more information.

    Returns
    -------
    dict
        A dictionary with keys representing faces and values representing their
        colors. Colors are identified by the integers $0,1,2,\\ldots$. The
        number of colors being used in a solution ``c`` is therefore
        ``max(c.values()) + 1``. Each face (key) is a tuple that gives the
        sequence of nodes that surround it. These correspond to cycles in
        ``G``. The first element in ``c`` defines the external face; the
        remainder defines the internal faces. For internal faces, the nodes
        are listed in a counterclockwise order; for the external face, the
        nodes are listed in a clockwise order.

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
    node_coloring
    face_coloring

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
    if k < 0:
        raise ValueError("Error, positive integer needed for k")
    _check_params(G, "dsatur", opt_alg, it_limit, verbose)
    if len(G) == 0 or G.number_of_edges() == 0:
        return {}
    H, faces = fc._get_dual(G, pos)
    c = node_k_coloring(H, k, opt_alg=opt_alg,
                        it_limit=it_limit, verbose=verbose)
    return {tuple(faces[i]): c[i] for i in range(len(H))}


def equitable_face_k_coloring(G, pos, k, opt_alg=None, it_limit=0, verbose=0):
    """Attempt to color the faces of a planar graph ``G`` using ``k`` colors.

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
        The faces of this graph will be colored.

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
        * ``None`` : No optimization is performed.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Only applicable
        when using ``opt_alg=2`` or ``opt_alg=3``.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process. The higher the value, the more information.

    Returns
    -------
    dict
        A dictionary with keys representing faces and values representing their
        colors. Colors are identified by the integers $0,1,2,\\ldots$. The
        number of colors being used in a solution ``c`` is therefore
        ``max(c.values()) + 1``. Each face (key) is a tuple that gives the
        sequence of nodes that surround it. These correspond to cycles in
        ``G``. The first element in ``c`` defines the external face; the
        remainder defines the internal faces. For internal faces, the nodes
        are listed in a counterclockwise order; for the external face, the
        nodes are listed in a clockwise order.

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
    node_coloring
    face_coloring

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
    if k < 0:
        raise ValueError("Error, nonnegative integer needed for k")
    _check_params(G, "dsatur", opt_alg, it_limit, verbose)
    if len(G) == 0 or G.number_of_edges() == 0:
        return {}
    H, faces = fc._get_dual(G, pos)
    c = equitable_node_k_coloring(
        H, k, weight=None, opt_alg=opt_alg, it_limit=it_limit, verbose=verbose
    )
    return {tuple(faces[i]): c[i] for i in range(len(H))}


def face_precoloring(
    G, pos, precol=None, strategy="dsatur", opt_alg=None, it_limit=0, verbose=0
):
    """Give a face coloring of a planar graph where some faces are precolored.

    A face coloring is an assignment of colors to the faces of a graph's
    planar embedding so that adjacent faces have different colors (a pair of
    faces is adjacent if and only if they share a bordering edge). The aim is
    to use as few colors as possible. Face colorings are only possible in
    planar embeddings; hence the graph ``G`` must be planar, and ``pos`` should
    give valid $(x,y)$ coordinates for all nodes.

    In the face precoloring problem, some of the faces have already been
    assigned colors. The aim is to allocate colors to the remaining faces so
    that we get a full face coloring that uses a minimum number of colors.

    In this implementation, face colorings of a graph $G$ are determined by
    forming $G$'s dual graph, and then passing the dual to the
    :meth:`node_precoloring` method. All parameters are therefore the same as
    the latter.

    Parameters
    ----------
    G : NetworkX graph
        The faces of this graph will be colored.

    pos : dict
        A dictionary of positions keyed by node. All positions should be
        $(x,y)$ coordinates, and none of the edges in the resultant embedding
        should be crossing.

    precol : None or dict, optional (default=None)
        A dictionary that specifies the colors of any precolored faces.
        Precolored faces are identified by using one or more of their
        surrounding arcs. Each internal face is characterized by the series
        of arcs that surround it in a counterclockwise direction. Similarly,
        the one external face is identified by the series of arcs traveling in
        a clockwise direction. Including one of these surrounding arcs in the
        precoloring is sufficient.

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
        * ``None`` : No optimization is performed.

    it_limit : int, optional (default=0)
        Number of iterations of the local search procedure. Only applicable
        when using ``opt_alg=2`` or ``opt_alg=3``.

    verbose : int, optional (default=0)
        If set to a positive value, information is output during the
        optimization process. The higher the value, the more information.

    Returns
    -------
    dict
        A dictionary with keys representing faces and values representing their
        colors. Colors are identified by the integers $0,1,2,\\ldots$. The
        number of colors being used in a solution ``c`` is therefore
        ``max(c.values()) + 1``. Each face (key) is a tuple that gives the
        sequence of nodes that surround it. These correspond to cycles in
        ``G``. The first element in ``c`` defines the external face; the
        remainder defines the internal faces. For internal faces, the nodes
        are listed in a counterclockwise order; for the external face, the
        nodes are listed in a clockwise order.

    Examples
    --------
    >>> import gcol
    >>> import networkx as nx
    >>>
    >>> G = nx.dodecahedral_graph()
    >>> pos = nx.planar_layout(G)
    >>> P = {(14,15): 0, (15,14): 1, (1,2): 0}
    >>> c = gcol.face_precoloring(G, pos, P)
    >>> print(c)
    {(1, 0, 10, 9, 8): 1, (10, 0, 19, 18, 11): 2, ..., (13, 12, 16, 15, 14): 1}

    Raises
    ------
    NotImplementedError
        If ``G`` is a directed graph or a multigraph.

        If ``G`` contains any self-loops.

    TypeError
        If ``pos`` is not a dictionary.

    ValueError
        If ``strategy`` is not among the supported options.

        If ``opt_alg`` is not among the supported options.

        If ``it_limit`` is not a nonnegative integer.

        If ``verbose`` is not a nonnegative integer.

        If ``precol`` contains an arc that is not in the embedding of ``G``.

        If ``precol`` contains a non-integer color label.

        If ``precol`` contains a pair of adjacent faces assigned to the same
        color.

        If ``precol`` uses an integer color label $j$, but there exists a color
        label $0 \\leq i < j$ that is not being used.

        If ``pos`` has missing or invalid entries.

        If ``pos`` does not specify a valid planar embedding of ``G``.

        If ``G`` is not planar or contains bridges.

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
    node_precoloring
    node_coloring

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
    if len(G) == 0 or G.number_of_edges() == 0:
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
    cols = set()
    for u, v in precol:
        if not G.has_edge(u, v):
            raise ValueError(
                "Error, an edge is defined in the precoloring that is not in "
                "the graph"
            )
        if not isinstance(precol[u, v], int):
            raise ValueError(
                "Error, all color labels in the precoloring should be integers"
            )
        cols.add(precol[u, v])
    k = max(precol.values()) + 1
    for i in range(k):
        if i not in cols:
            raise ValueError(
                "Error, the color labels in the precoloring should be in "
                "{0,1,2,...} and each color should be being used by at least "
                "one face"
            )
    H, faces = fc._get_dual(G, pos)
    arcFace = {}
    for i in range(len(faces)):
        for j in range(len(faces[i])):
            arcFace[(faces[i][j], faces[i][(j + 1) % len(faces[i])])] = i
    arcs = list(precol.keys())
    for i in range(len(arcs)-1):
        for j in range(i+1, len(arcs)):
            if (arcFace[arcs[i]] == arcFace[arcs[j]] and
                    precol[arcs[i]] != precol[arcs[j]]):
                raise ValueError(
                    "Error, arcs specified in precol that belong to the same "
                    "face but are given different colors. This means that the "
                    "same face as been preassigned to more than one color"
                )
    P = {arcFace[arc]: precol[arc] for arc in precol}
    c = node_precoloring(
        H, precol=P, strategy=strategy, opt_alg=opt_alg, it_limit=it_limit,
        verbose=verbose
    )
    return {tuple(faces[i]): c[i] for i in range(len(H))}


# Alternative spellings of the above methods and globals
colouring_layout = coloring_layout
edge_colouring = edge_coloring
edge_k_colouring = edge_k_coloring
edge_precolouring = edge_precoloring
equitable_edge_k_colouring = equitable_edge_k_coloring
equitable_node_k_colouring = equitable_node_k_coloring
get_edge_colours = get_edge_colors
get_node_colours = get_node_colors
get_set_colours = get_set_colors
min_cost_k_colouring = min_cost_k_coloring
node_colouring = node_coloring
node_k_colouring = node_k_coloring
node_precolouring = node_precoloring
face_colouring = face_coloring
face_k_colouring = face_k_coloring
face_precolouring = face_precoloring
equitable_face_k_colouring = equitable_face_k_coloring
colourful = colorful
colourblind = colorblind

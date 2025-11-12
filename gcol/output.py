import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

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


def _all_numeric(L):
    # Returns True iff all items in the list are numeric values
    return all(isinstance(x, (int, float)) for x in L)


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


# Alternative spellings of the above methods and globals
colouring_layout = coloring_layout
get_node_colours = get_node_colors
get_edge_colours = get_edge_colors
get_set_colours = get_set_colors
draw_face_colouring = draw_face_coloring
colourful = colorful
colourblind = colorblind

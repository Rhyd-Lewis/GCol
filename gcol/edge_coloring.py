import networkx as nx
import random
from .node_coloring import equitable_node_k_coloring, node_k_coloring, _greedy
from .node_coloring import _rlf, _dsatur, _getEdgeWeights, _getNodeWeights
from .node_coloring import _reducecolors, _backtrackcol, node_precoloring
from .node_coloring import _check_params


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
    :meth:`gcol.node_coloring.node_k_coloring`
    :meth:`gcol.node_coloring.equitable_node_k_coloring`
    :meth:`gcol.node_coloring.kempe_chain`

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
    _check_params(G, "dsatur", opt_alg, it_limit, verbose)
    if k < 0:
        raise ValueError("Error, nonnegative integer needed for k")
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
    algorithm (based on backtracking), or a choice of four polynomial-time
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
    :meth:`gcol.node_coloring.node_k_coloring`

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
    _check_params(G, "dsatur", opt_alg, it_limit, verbose)
    if k < 0:
        raise ValueError("Error, positive integer needed for k")
    if len(G) == 0 or G.number_of_edges() == 0:
        return {}
    maxdeg = max(d for v, d in G.degree())
    if k < maxdeg:
        raise ValueError(
            "Error, a k-coloring of this graph does not exist. "
            "Try increasing k"
        )
    H = nx.line_graph(G)
    return node_k_coloring(
        H, k, opt_alg=opt_alg, it_limit=it_limit, verbose=verbose
    )


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
    four polynomial-time heuristic algorithms (based on local search). The
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
    chromatic_index
    edge_k_coloring
    :meth:`gcol.node_coloring.node_coloring`

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
        c = _greedy(H, V)
    elif strategy == "welsh_powell":
        V = sorted(H, key=H.degree, reverse=True)
        c = _greedy(H, V)
    elif strategy == "rlf":
        c = _rlf(H)
    else:
        c = _dsatur(H)
    # If selected, employ the chosen optimisation method
    if opt_alg is None:
        return c
    if opt_alg in [2, 4]:
        W = _getEdgeWeights(H, None)
    else:
        W = _getNodeWeights(H, None)
    cliqueNum = nx.approximation.large_clique_size(H)
    return _reducecolors(
        H, c, max(cliqueNum, maxdeg), W, opt_alg, it_limit, verbose
    )


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
    :meth:`gcol.node_coloring.chromatic_number`
    :meth:`gcol.node_coloring.node_coloring`

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
    c = _backtrackcol(H, max(cliqueNum, maxdeg), 0)
    return max(c.values()) + 1


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
    backtracking), or a choice of four polynomial-time heuristic algorithms
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
    :meth:`gcol.node_coloring.node_precoloring`
    :meth:`gcol.node_coloring.node_coloring`

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


# Alternative spellings of the above methods
edge_colouring = edge_coloring
edge_k_colouring = edge_k_coloring
edge_precolouring = edge_precoloring
equitable_edge_k_colouring = equitable_edge_k_coloring

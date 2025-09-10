"""Greedy coloring test suite."""
import pytest
import networkx as nx
from collections import defaultdict
import gcol


GREEDY_METHODS = ["random", "welsh_powell", "dsatur", "rlf"]
OPT_ALGS = [1, 2, 3, None]
IT_LIMITS = [0, 100, 1000]
VERBOSE = [0, 1, 2]


class TestColorings:
    def test_many(self):
        for graph_func in TEST_CASES:
            G = graph_func()
            for strategy in GREEDY_METHODS:
                for opt_alg in OPT_ALGS:
                    for it_limit in IT_LIMITS:
                        for verbose in VERBOSE:
                            c = gcol.node_coloring(
                                G,
                                strategy=strategy,
                                opt_alg=opt_alg,
                                it_limit=it_limit,
                                verbose=verbose
                            )
                            assert verify_node_coloring(G, c)
                            c = gcol.node_colouring(
                                G,
                                strategy=strategy,
                                opt_alg=opt_alg,
                                it_limit=it_limit,
                                verbose=verbose
                            )
                            assert verify_node_coloring(G, c)
                            c = gcol.edge_coloring(
                                G,
                                strategy=strategy,
                                opt_alg=opt_alg,
                                it_limit=it_limit,
                                verbose=verbose
                            )
                            assert verify_edge_coloring(G, c)
                            c = gcol.edge_colouring(
                                G,
                                strategy=strategy,
                                opt_alg=opt_alg,
                                it_limit=it_limit,
                                verbose=verbose
                            )
                            assert verify_edge_coloring(G, c)

    def test_bad_strategy(self):
        graph = singleton()
        pytest.raises(
            ValueError,
            gcol.node_coloring,
            graph,
            strategy="this is an invalid strategy",
        )

    def test_bad_opt_alg(self):
        graph = singleton()
        pytest.raises(
            ValueError,
            gcol.node_coloring,
            graph,
            opt_alg="this is an invalid optimisation algorithm",
        )

    def test_bad_its_parameter(self):
        graph = singleton()
        pytest.raises(
            ValueError,
            gcol.node_coloring,
            graph,
            it_limit="this is not an integer",
        )

    def test_negative_tabu_parameter(self):
        graph = singleton()
        pytest.raises(ValueError, gcol.node_coloring, graph, it_limit=-1)

    def test_bad_verbose_parameter(self):
        graph = singleton()
        pytest.raises(
            ValueError,
            gcol.node_coloring,
            graph,
            opt_alg=1,
            verbose="this is not an integer"
        )

    def test_negative_verbose_parameter(self):
        graph = singleton()
        pytest.raises(ValueError, gcol.node_coloring, graph, verbose=-1)

    def test_directed_graph(self):
        graph = nx.erdos_renyi_graph(10, 0.5, directed=True)
        pytest.raises(NotImplementedError, gcol.node_coloring, graph)

    def test_multigraph(self):
        graph = nx.MultiGraph()
        graph.add_edges_from(
            [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 1), (0, 1)])
        pytest.raises(NotImplementedError, gcol.node_coloring, graph)

    def test_loops(self):
        graph = nx.complete_graph(3)
        graph.add_edge(0, 0)
        pytest.raises(NotImplementedError, gcol.node_coloring, graph)


class TestChromatics:
    def test_many_chromatic_number(self):
        for graph_func in TEST_CASES:
            G = graph_func()
            chi = gcol.chromatic_number(G)
            assert chi >= 0 and chi <= G.number_of_nodes()

    def test_many_chromatic_index(self):
        for graph_func in TEST_CASES:
            G = graph_func()
            chi = gcol.chromatic_index(G)
            delta = get_max_degree(G)
            assert chi == delta or chi == delta + 1


class TestNodePrecolorings:
    def test_many(self):
        for graph_func in TEST_CASES:
            G = graph_func()
            # color all nodes, then uncolor some to get a valid precoloring
            precol = gcol.node_coloring(G, strategy="random")
            colSize = defaultdict(int)
            for u in precol:
                colSize[precol[u]] += 1
            V = list(precol)
            for i in range(len(V)):
                u = V[i]
                if i % 2 == 0 and colSize[precol[u]] > 1:
                    colSize[precol[u]] -= 1
                    del precol[u]
            for strategy in GREEDY_METHODS:
                for opt_alg in OPT_ALGS:
                    for it_limit in IT_LIMITS:
                        c = gcol.node_precoloring(
                            G,
                            precol,
                            strategy=strategy,
                            opt_alg=opt_alg,
                            it_limit=it_limit,
                        )
                        assert verify_node_coloring(G, c, precol)
                        c = gcol.node_precolouring(
                            G,
                            precol,
                            strategy=strategy,
                            opt_alg=opt_alg,
                            it_limit=it_limit,
                        )
                        assert verify_node_coloring(G, c, precol)
                        c = gcol.node_precoloring(
                            G,
                            None,
                            strategy=strategy,
                            opt_alg=opt_alg,
                            it_limit=it_limit,
                        )
                        assert verify_node_coloring(G, c)
                        c = gcol.node_precoloring(
                            G,
                            {},
                            strategy=strategy,
                            opt_alg=opt_alg,
                            it_limit=it_limit
                        )
                        assert verify_node_coloring(G, c, {})

    def test_bad_precol1(self):
        graph = singleton()
        pytest.raises(TypeError, gcol.node_precoloring,
                      graph, precol="this is not a dict")

    def test_bad_precol2(self):
        graph = three_node_clique()
        pytest.raises(ValueError, gcol.node_precoloring, graph, precol={4: 1})

    def test_bad_precol3(self):
        graph = three_node_clique()
        pytest.raises(ValueError, gcol.node_precoloring,
                      graph, precol={0: "color 5"})

    def test_bad_precol4(self):
        graph = three_node_clique()
        pytest.raises(ValueError, gcol.node_precoloring,
                      graph, precol={0: 0, 1: 0})

    def test_bad_precol5(self):
        graph = three_node_clique()
        pytest.raises(ValueError, gcol.node_precoloring,
                      graph, precol={0: 0, 1: 3})


class TestEdgePrecolorings:
    def test_many(self):
        for graph_func in TEST_CASES:
            G = graph_func()
            # color all nodes, then uncolor some to get a valid precoloring
            precol = gcol.edge_coloring(G, strategy="random")
            colSize = defaultdict(int)
            for e in precol:
                colSize[precol[e]] += 1
            E = list(precol)
            for i in range(len(E)):
                e = E[i]
                if i % 2 == 0 and colSize[precol[e]] > 1:
                    colSize[precol[e]] -= 1
                    del precol[e]
            for strategy in GREEDY_METHODS:
                for opt_alg in OPT_ALGS:
                    for it_limit in IT_LIMITS:
                        c = gcol.edge_precoloring(
                            G,
                            precol,
                            strategy=strategy,
                            opt_alg=opt_alg,
                            it_limit=it_limit,
                        )
                        assert verify_edge_coloring(G, c, precol)
                        c = gcol.edge_precolouring(
                            G,
                            precol,
                            strategy=strategy,
                            opt_alg=opt_alg,
                            it_limit=it_limit,
                        )
                        assert verify_edge_coloring(G, c, precol)
                        c = gcol.edge_precoloring(
                            G,
                            None,
                            strategy=strategy,
                            opt_alg=opt_alg,
                            it_limit=it_limit,
                        )
                        assert verify_edge_coloring(G, c)
                        c = gcol.edge_precoloring(
                            G,
                            {},
                            strategy=strategy,
                            opt_alg=opt_alg,
                            it_limit=it_limit
                        )
                        assert verify_edge_coloring(G, c, {})

    def test_bad_precol1(self):
        graph = three_node_clique()
        pytest.raises(TypeError, gcol.edge_precoloring,
                      graph, precol="this is not a dict")

    def test_bad_precol2(self):
        graph = three_node_clique()
        pytest.raises(ValueError, gcol.edge_precoloring,
                      graph, precol={(1, 4): 1})

    def test_bad_precol3(self):
        graph = three_node_clique()
        pytest.raises(ValueError, gcol.edge_precoloring,
                      graph, precol={(0, 1): "color 5"})

    def test_bad_precol4(self):
        graph = three_node_clique()
        pytest.raises(ValueError, gcol.edge_precoloring,
                      graph, precol={(0, 1): 0, (1, 2): 0})

    def test_bad_precol5(self):
        graph = three_node_clique()
        pytest.raises(ValueError, gcol.edge_precoloring,
                      graph, precol={(0, 1): 0, (1, 2): 3})


class TestKempeChain:
    def test_many(self):
        for graph_func in TEST_CASES:
            G = graph_func()
            c = gcol.node_coloring(G, strategy="random")
            k = get_num_cols(c)
            for u in G:
                for j in range(k):
                    gcol.kempe_chain(G, c, u, j)

    def test_clashing_col(self):
        graph = nx.erdos_renyi_graph(10, 1.0)
        c = {v: 0 for v in graph}
        pytest.raises(ValueError, gcol.kempe_chain, graph, c, 0, 0)

    def test_bad_s(self):
        graph = nx.erdos_renyi_graph(10, 1.0)
        c = gcol.node_coloring(graph, strategy="random")
        pytest.raises(ValueError, gcol.kempe_chain, graph, c, 999, 0)


class TestKColourings:
    def test_many(self):
        for graph_func in TEST_CASES:
            G = graph_func()
            for opt_alg in OPT_ALGS:
                for it_limit in IT_LIMITS:
                    c = gcol.node_k_coloring(
                        G, len(G), opt_alg=opt_alg, it_limit=it_limit
                    )
                    assert verify_node_coloring(G, c)
                    c = gcol.node_k_colouring(
                        G, len(G), opt_alg=opt_alg, it_limit=it_limit
                    )
                    assert verify_node_coloring(G, c)
                    c = gcol.edge_k_coloring(
                        G,
                        get_max_degree(G) + 1,
                        opt_alg=opt_alg,
                        it_limit=it_limit
                    )
                    assert verify_edge_coloring(G, c)
                    c = gcol.edge_k_colouring(
                        G,
                        get_max_degree(G) + 1,
                        opt_alg=opt_alg,
                        it_limit=it_limit
                    )
                    assert verify_edge_coloring(G, c)
                    c = gcol.equitable_node_k_coloring(
                        G,
                        len(G),
                        weight=None,
                        opt_alg=opt_alg,
                        it_limit=it_limit
                    )
                    assert verify_node_coloring(G, c)
                    c = gcol.equitable_edge_k_coloring(
                        G,
                        get_max_degree(G) + 1,
                        weight=None,
                        opt_alg=opt_alg,
                        it_limit=it_limit,
                    )
                    assert verify_edge_coloring(G, c)

    def test_bad_k_1(self):
        graph = three_node_clique()
        pytest.raises(ValueError, gcol.node_k_coloring, graph, 2)
        pytest.raises(ValueError, gcol.edge_k_coloring, graph, 2)
        pytest.raises(ValueError, gcol.equitable_node_k_coloring, graph, 2)
        pytest.raises(ValueError, gcol.equitable_edge_k_coloring, graph, 2)

    def test_bad_k_2(self):
        graph = three_node_clique()
        pytest.raises(ValueError, gcol.node_k_coloring, graph, -2)
        pytest.raises(ValueError, gcol.edge_k_coloring, graph, -2)
        pytest.raises(ValueError, gcol.equitable_node_k_coloring, graph, -2)
        pytest.raises(ValueError, gcol.equitable_edge_k_coloring, graph, -2)

    def test_bad_node_weights(self):
        graph = nx.Graph()
        graph.add_nodes_from([0, 1, 2], weight=-5)
        graph.add_edges_from([(0, 1), (1, 2), (2, 0)])
        pytest.raises(
            ValueError,
            gcol.equitable_node_k_coloring, graph, 3, weight="weight"
        )

    def test_bad_edge_weights(self):
        graph = nx.Graph()
        graph.add_nodes_from([0, 1, 2])
        graph.add_edges_from([(0, 1), (1, 2), (2, 0)], weight=-5)
        pytest.raises(
            ValueError,
            gcol.equitable_edge_k_coloring, graph, 3, weight="weight"
        )


class TestMaxIS:
    def test_many(self):
        for graph_func in TEST_CASES:
            G = graph_func()
            for it_limit in IT_LIMITS:
                S = gcol.max_independent_set(G, weight=None, it_limit=it_limit)
                assert verify_independent_set(G, S)


class TestMinCostKColoring:
    def test_many(self):
        for graph_func in TEST_CASES:
            G = graph_func()
            for u in G:
                for v in G[u]:
                    G[u][v]["weight"] = 3
            for it_limit in IT_LIMITS:
                for k in range(1, len(G) + 1):
                    gcol.min_cost_k_coloring(
                        G,
                        k,
                        weight=None,
                        weights_at="nodes",
                        it_limit=it_limit
                    )
                    gcol.min_cost_k_colouring(
                        G,
                        k,
                        weight=None,
                        weights_at="nodes",
                        it_limit=it_limit
                    )
                for k in range(2, len(G) + 1):
                    gcol.min_cost_k_coloring(
                        G,
                        k,
                        weight=None,
                        weights_at="edges",
                        it_limit=it_limit
                    )
                    gcol.min_cost_k_colouring(
                        G,
                        k,
                        weight=None,
                        weights_at="edges",
                        it_limit=it_limit
                    )
                for k in range(2, len(G) + 1):
                    gcol.min_cost_k_coloring(
                        G,
                        k,
                        weight="weight",
                        weights_at="edges",
                        it_limit=it_limit
                    )
                    gcol.min_cost_k_colouring(
                        G,
                        k,
                        weight="weight",
                        weights_at="edges",
                        it_limit=it_limit
                    )

    def test_bad_node_weights(self):
        graph = nx.Graph()
        graph.add_nodes_from([0, 1, 2], weight=-5)
        graph.add_edges_from([(0, 1), (1, 2), (2, 0)])
        pytest.raises(
            ValueError,
            gcol.min_cost_k_coloring,
            graph,
            3,
            weight="weight",
            weights_at="nodes",
        )

    def test_bad_edge_weight(self):
        graph = nx.Graph()
        graph.add_nodes_from([0, 1, 2])
        graph.add_edges_from([(0, 1), (1, 2), (2, 0)], weight=-5)
        pytest.raises(
            ValueError,
            gcol.min_cost_k_coloring,
            graph,
            3,
            weight="weight",
            weights_at="edges",
        )

    def test_bad_node_weight_labels(self):
        graph = nx.Graph()
        graph.add_nodes_from([0, 1, 2], weight=5)
        graph.add_edges_from([(0, 1), (1, 2), (2, 0)])
        pytest.raises(
            ValueError,
            gcol.min_cost_k_coloring,
            graph,
            3,
            weight="wait",
            weights_at="nodes",
        )

    def test_bad_edge_weight_labels(self):
        graph = nx.Graph()
        graph.add_nodes_from([0, 1, 2])
        graph.add_edges_from([(0, 1), (1, 2), (2, 0)], weight=5)
        pytest.raises(
            ValueError,
            gcol.min_cost_k_coloring,
            graph,
            3,
            weight="wait",
            weights_at="edges",
        )


class TestFaceColorings:

    def test_many(self):
        for graph_func in FACE_TEST_CASES:
            G = graph_func()
            pos = nx.planar_layout(G)
            for strategy in GREEDY_METHODS:
                for opt_alg in OPT_ALGS:
                    for it_limit in IT_LIMITS:
                        gcol.face_coloring(
                            G,
                            pos,
                            strategy=strategy,
                            opt_alg=opt_alg,
                            it_limit=it_limit
                        )
                        gcol.face_colouring(
                            G,
                            pos,
                            strategy=strategy,
                            opt_alg=opt_alg,
                            it_limit=it_limit
                        )

    def test_bad_strategy(self):
        graph = singleton()
        pos = {0: (0, 0)}
        pytest.raises(
            ValueError,
            gcol.face_coloring,
            graph,
            pos,
            strategy="this is an invalid strategy",
        )

    def test_bad_opt_alg(self):
        graph = singleton()
        pos = {0: (0, 0)}
        pytest.raises(
            ValueError,
            gcol.face_coloring,
            graph,
            pos,
            opt_alg="this is an invalid optimisation algorithm",
        )

    def test_bad_its_parameter(self):
        graph = singleton()
        pos = {0: (0, 0)}
        pytest.raises(
            ValueError,
            gcol.face_coloring,
            graph,
            pos,
            it_limit="this is not an integer",
        )

    def test_negative_tabu_parameter(self):
        graph = singleton()
        pos = {0: (0, 0)}
        pytest.raises(ValueError, gcol.face_coloring, graph, pos, it_limit=-1)

    def test_directed_graph(self):
        graph = nx.erdos_renyi_graph(3, 1.0, directed=True)
        pos = {0: (0, 0), 1: (1, 1), 3: (1, 0)}
        pytest.raises(NotImplementedError, gcol.face_coloring, graph, pos)

    def test_multigraph(self):
        graph = nx.MultiGraph()
        graph.add_edges_from(
            [(0, 1), (0, 1)])
        pos = {0: (0, 0), 1: (1, 1)}
        pytest.raises(NotImplementedError, gcol.face_coloring, graph, pos)

    def test_invalid_pos(self):
        graph = nx.complete_graph(3)
        pos = "I am not a dict"
        pytest.raises(TypeError, gcol.face_coloring, graph, pos)

    def test_missing_pos(self):
        graph = nx.complete_graph(3)
        pos = {0: (0, 0), 1: (1, 0)}
        pytest.raises(ValueError, gcol.face_coloring, graph, pos)

    def test_duplicate_pos(self):
        graph = nx.complete_graph(3)
        pos = {0: (0, 0), 1: (1, 0), 2: (1, 0)}
        pytest.raises(ValueError, gcol.face_coloring, graph, pos)

    def test_not_planar(self):
        graph = nx.complete_graph(4)
        pos = {0: (0, 0), 1: (1, 0), 2: (0, 1), 3: (1, 1)}
        pytest.raises(ValueError, gcol.face_coloring, graph, pos)

    def test_has_bridges(self):
        graph = nx.path_graph(3)
        pos = {0: (0, 0), 1: (1, 0), 2: (0, 1)}
        pytest.raises(ValueError, gcol.face_coloring, graph, pos)

    def test_not_embedding(self):
        graph = nx.cycle_graph(4)
        pos = {0: (0, 0), 1: (1, 0), 2: (0, 1), 3: (1, 1)}
        pytest.raises(ValueError, gcol.face_coloring, graph, pos)

    def test_not_embedding2(self):
        graph = nx.cycle_graph(4)
        pos = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (2, 0)}
        pytest.raises(ValueError, gcol.face_coloring, graph, pos)

    def test_precol_invalid_arg(self):
        graph = nx.cycle_graph(4)
        graph.add_edge(0, 2)
        pos = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}
        precol = "I am not a dict"
        pytest.raises(TypeError, gcol.face_precoloring, graph, pos, precol)

    def test_precol_invalid_edge(self):
        graph = nx.cycle_graph(4)
        graph.add_edge(0, 2)
        pos = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}
        precol = {(1, 3): 1}
        pytest.raises(ValueError, gcol.face_precoloring, graph, pos, precol)

    def test_precol_invalid_col(self):
        graph = nx.cycle_graph(4)
        graph.add_edge(0, 2)
        pos = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}
        precol = {(1, 2): 0.5}
        pytest.raises(ValueError, gcol.face_precoloring, graph, pos, precol)

    def test_precol_invalid_col2(self):
        graph = nx.cycle_graph(4)
        graph.add_edge(0, 2)
        pos = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}
        precol = {(1, 2): 1}
        pytest.raises(ValueError, gcol.face_precoloring, graph, pos, precol)

    def test_precol_invalid_col3(self):
        graph = nx.cycle_graph(4)
        graph.add_edge(0, 2)
        pos = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}
        precol = {(1, 0): 0, (2, 1): 1}
        pytest.raises(ValueError, gcol.face_precoloring, graph, pos, precol)


# Utility functions
def verify_node_coloring(G, c, precol=None):
    if len(c) != 0:
        k = max(c.values()) + 1
        used = set()
        for v in c:
            assert (
                c[v] >= 0 and c[v] < k
            ), "Node assigned to a color not in {0,1,...,k-1}"
            used.add(c[v])
        assert len(used) == k, "Unused colors in {0,1,...,k-1}"
        for u in G:
            for v in G[u]:
                assert c[u] != c[v], "Adjacent nodes have the same color"
        if precol is not None:
            for v in precol:
                assert (
                    c[v] == precol[v]
                ), "Error a precolored node is not colored correctly"
    gcol.partition(c)
    gcol.get_node_colors(G, c)
    return True


def verify_edge_coloring(G, c, precol=None):
    if len(c) != 0:
        k = max(c.values()) + 1
        used = set()
        for e in c:
            assert (
                c[e] >= 0 and c[e] < k
            ), "Edge assigned to a color not in {0,1,...,k-1}"
            used.add(c[e])
        assert len(used) == k, "Unused colors in {0,1,...,k-1}"
        for e1 in G.edges:
            for e2 in G.edges:
                if e1 != e2:
                    if (
                        e1[0] == e2[0]
                        or e1[0] == e2[1]
                        or e1[1] == e2[0]
                        or e1[1] == e2[1]
                    ):
                        assert c[e1] != c[e2], "Adjacent edges are same color"
        if precol is not None:
            for u, v in precol:
                assert (
                    c[u, v] == precol[u, v]
                ), "Error a precolored edge is not colored correctly"
    gcol.partition(c)
    gcol.get_edge_colors(G, c)
    return True


def verify_independent_set(G, S):
    for u in G:
        for v in G[u]:
            assert not (
                u in S and v in S
            ), "Adjacent nodes present in the independent set S"
    gcol.get_set_colors(G, S)
    return True


def get_max_degree(G):
    # Get the maximum degree in G
    return max(G.degree(node) for node in G.nodes) if len(G.nodes) > 0 else 0


def get_num_cols(c):
    if len(c) == 0:
        return 0
    return max(c.values()) + 1


# Different graphs to test
def null_graph():
    return nx.Graph()


def singleton():
    graph = nx.Graph()
    graph.add_node(0)
    return graph


def dyad():
    graph = nx.Graph()
    graph.add_edge(0, 1)
    return graph


def three_node_clique():
    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (1, 2), (2, 0)])
    return graph


def disconnected():
    graph = nx.Graph()
    graph.add_edges_from([(1, 2), (2, 3), (4, 5), (5, 6)])
    return graph


def mixed_names():
    graph = nx.Graph()
    graph.add_nodes_from([0, 1, "node-A", ("A", 3)])
    graph.add_edges_from([(0, 1), (1, "node-A"),
                          ("node-A", ("A", 3)), (0, ("A", 3))])
    return graph


def empty():
    return nx.erdos_renyi_graph(10, 0.0, 1)


def sparse():
    return nx.erdos_renyi_graph(10, 0.1, 1)


def medium():
    return nx.erdos_renyi_graph(10, 0.5, 1)


def dense():
    return nx.erdos_renyi_graph(10, 0.9, 1)


def complete():
    return nx.erdos_renyi_graph(10, 1.0, 1)


def complete_bipartite():
    graph = nx.Graph()
    for u in range(0, 10, 2):
        for v in range(1, 11, 2):
            graph.add_edge(u, v)
    return graph


def dodec():
    return nx.dodecahedral_graph()


def grid():
    return nx.grid_2d_graph(3, 4)


# --------------------------------------------------------------------------
# Test graphs
TEST_CASES = [
    null_graph,
    singleton,
    dyad,
    disconnected,
    three_node_clique,
    mixed_names,
    empty,
    sparse,
    medium,
    dense,
    complete,
    complete_bipartite,
    dodec,
    grid,
]

FACE_TEST_CASES = [
    null_graph,
    singleton,
    three_node_clique,
    mixed_names,
    empty,
    dodec,
    grid,
]

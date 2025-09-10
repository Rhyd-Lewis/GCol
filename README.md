# GCol

[![DOI](https://joss.theoj.org/papers/10.21105/joss.07871/status.svg)](https://doi.org/10.21105/joss.07871)

GCol is an open-source Python library for graph coloring, built on top
of NetworkX. It provides easy-to-use, high-performance algorithms for
node coloring, edge coloring, face coloring, equitable coloring, 
weighted coloring, precoloring, and maximum independent set 
identification. It also offers several tools for solution visualization.

In general, graph coloring problems are NP-hard. This library therefore
offers both exponential-time exact algorithms and polynomial-time
heuristic algorithms.

## Quick Start

To install the GCol library, type the following at the command prompt:

    python -m pip install gcol

or execute the following in a notebook:

    !python -m pip install gcol

To start using this library, try executing the following code.

```python
import networkx as nx
import matplotlib.pyplot as plt
import gcol

G = nx.dodecahedral_graph()
c = gcol.node_coloring(G)
print("Here is a node coloring of graph G:", c)
nx.draw_networkx(G, node_color=gcol.get_node_colors(G, c))
plt.show()
```

## Textbook

The algorithms and techniques used in this library are based on the 2021
textbook by Lewis, R. M. R. (2021) [A Guide to Graph Colouring:
Algorithms and
Applications](https://link.springer.com/book/10.1007/978-3-030-81054-2),
Springer Cham. (2nd Edition). In bibtex, this book is cited as:

    @book{10.1007/978-3-030-81054-2,
      author = {Lewis, R. M. R.},
      title = {A Guide to Graph Colouring: Algorithms and Applications},
      year = {2021},
      isbn = {978-3-030-81056-6},
      publisher = {Springer Cham},
      edition = {2nd}
    }

## Support

The GCol repository is hosted on 
[github](https://github.com/Rhyd-Lewis/GCol). If you have any questions 
or issues, please ask them on [stackoverflow](https://stackoverflow.com), 
adding the tag `graph-coloring`. All documentation is listed on 
[this website](https://gcol.readthedocs.io/en/latest/) or, if you prefer in, 
[this pdf](https://readthedocs.org/projects/gcol/downloads/pdf/latest/).
If you have any suggestions for this library or notice any bugs, please 
contact the author using the contact details at [www.rhydlewis.eu](http://www.rhydlewis.eu).

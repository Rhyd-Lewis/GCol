# GCol

GCol is an open-source Python library for graph coloring, built on top
of NetworkX. It provides easy-to-use, high-performance algorithms for
node coloring, edge coloring, equitable coloring, weighted coloring,
precoloring, and maximum independent set identification. It also offers
several tools for solution visualization.

In general, graph coloring problems are NP-hard. This library therefore
offers both exponential-time exact algorithms and polynomial-time
heuristic algorithms.

GCol currently requires Python 3.7 or above. It also requires an
installation of NetworkX (ideally version 3.4 or above). To install the
GCol library from the [Python Package Index (PyPi)](https://pypi.org/),
run the following command at the command prompt:

    python -m pip install gcol
	
or execute the following in a notebook:

	!python -m pip install gcol

The algorithms and techniques used in this library are based on the 2021
textbook by Lewis, R. M. R. (2021) [A Guide to Graph Colouring:
Algorithms and
Applications](https://link.springer.com/book/10.1007/978-3-030-81054-2)
Springer Cham. (2nd Edition). In bibtex, this book can be cited as:

    @book{10.1007/978-3-030-81054-2,
      author = {Lewis, R. M. R.},
      title = {A Guide to Graph Colouring: Algorithms and Applications},
      year = {2021},
      isbn = {978-3-030-81056-6},
      publisher = {Springer Cham},
      edition = {2nd}
    }

## Support

The GCol repository is hosted on github
[here](https://github.com/Rhyd-Lewis/GCol). Its documentation can be
found on [this website](https://gcol.readthedocs.io/en/latest/) and in 
[this pdf](https://readthedocs.org/projects/gcol/downloads/pdf/latest/).

If you have any questions or issues, please ask them on 
[stackoverflow](https://stackoverflow.com), making sure to add the tag
`graph-coloring`.

## Simple example

```python
>>> import networkx as nx 
>>> import gcol 
>>> G = nx.dodecahedral_graph() 
>>> c = gcol.node_coloring(G) 
>>> print(c) 
{0: 0, 1: 1, 19: 1, 10: 1, 2: 0, 3: 2, 8: 0, 9: 2, 18: 0, 11: 2, 6: 1, 
7: 2, 4: 0, 5: 2, 13: 0, 12: 1, 14: 1, 15: 0, 16: 2, 17: 1}
>>> print(gcol.partition(c)) 
[0, 2, 4, 8, 13, 15, 18], [1, 6, 10, 12, 14, 17, 19], [3, 5, 7, 
9, 11, 16]]
```

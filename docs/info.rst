General Info
============

Welcome to the documentation of GCol -- a Python library for graph coloring! 

Quick Start
-----------

To install the GCol library, type the following at a command prompt::

    python -m pip install gcol

or execute the following in a notebook::

    !python -m pip install gcol

To start using this library, try executing the following code.

.. code:: ipython3

    import networkx as nx
    import matplotlib.pyplot as plt
    import gcol
    
    G = nx.dodecahedral_graph()
    c = gcol.node_coloring(G)
    print("Here is a node coloring of graph G:", c)
    nx.draw_networkx(G, node_color=gcol.get_node_colors(G, c))
    plt.show()

:doc:`This demonstration <demo/Demo>` gives further examples. You may also find it useful to consult the user guide of `NetworkX <https://networkx.org/>`_, as GCol makes use of its data structures and functionality.

Textbook
--------

The algorithms and techniques used in this library are based on the 2021 textbook by Lewis, R. M. R. (2021) `A Guide to Graph Colouring: Algorithms and Applications <https://link.springer.com/book/10.1007/978-3-030-81054-2>`_, Springer Cham. (2nd Edition). In bibtex, this book is cited as:: 

    @book{10.1007/978-3-030-81054-2,
      author = {Lewis, R. M. R.},
      title = {A Guide to Graph Colouring: Algorithms and Applications},
      year = {2021},
      isbn = {978-3-030-81056-6},
      publisher = {Springer Cham},
      edition = {2nd}
    }

Support
-------
The GCol repository is hosted on `github <https://github.com/Rhyd-Lewis/GCol>`_. If you have any questions, please ask them on `stackoverflow <https://stackoverflow.com>`_ adding the tag ``graph-coloring``. All documentation is listed `on this website <https://gcol.readthedocs.io/en/latest/>`_ or, if you prefer, `in this pdf document <https://readthedocs.org/projects/gcol/downloads/pdf/latest/>`_. If you have any suggestions for this library or notice any bugs, please contact the author using the contact details at `www.rhydlewis.eu <https://www.rhydlewis.eu>`_.

MIT License
-----------
Copyright (c) 2025 Rhyd-Lewis, Cardiff University, `www.rhydlewis.eu <https://www.rhydlewis.eu>`_.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

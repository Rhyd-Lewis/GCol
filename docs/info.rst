General Info
============

GCol currently requires Python 3.7 or above. It also requires an installation of NetworkX (ideally version 3.4 or above). To install the library from the Python Package Index (`PyPi <https://pypi.org/>`_), run the following command in a command prompt::

    python -m pip install gcol
	
or execute the following command in a notebook::

	!python -m pip install gcol

The algorithms and techniques used in this library are based on the 2021 textbook by Lewis, R. M. R. (2021) `A Guide to Graph Colouring: Algorithms and Applications <https://link.springer.com/book/10.1007/978-3-030-81054-2>`_, Springer Cham. (2nd Edition). In bibtex, this book can be cited as:: 

	@book{10.1007/978-3-030-81054-2,
	  author = {Lewis, R. M. R.},
	  title = {A Guide to Graph Colouring: Algorithms and Applications},
	  year = {2021},
	  isbn = {978-3-030-81056-6},
	  publisher = {Springer Cham},
	  edition = {2nd}
	}

To start using this library, you might find it helpful to look at this :doc:`demonstration <demo/Demo>`, which gives step-by-step instructions and sample code. You may also want to consult the user guide of `NetworkX <https://networkx.org/>`_, because GCol makes use of its data structures and functionality.

Support
-------
The GCol repository is hosted on `github <https://github.com/Rhyd-Lewis/GCol>`_. If you have any questions, please ask them on `stackoverflow <https://stackoverflow.com>`_ adding the tag ``graph-coloring``. All documentation is listed `on this website <https://gcol.readthedocs.io/en/latest/>`_ and `in this pdf document <https://readthedocs.org/projects/gcol/downloads/pdf/latest/>`_.

MIT License
-----------
Copyright (c) 2024 Rhyd-Lewis, Cardiff University, `www.rhydlewis.eu <https://www.rhydlewis.eu>`_.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Performance Analysis
====================

In this notebook we analyze the behavior of the various node coloring
algorithms in the ``gcol`` library. Where appropriate, we also make
comparisons to similar algorithms from the ``networkx`` library.

In this analysis, algorithms are evaluated by looking at solution
quality and run times. Details on asymptotic algorithm complexity (in
terms of big O notation) can be found in ``gcol``\ ’s documentation.
Here, all tests are conducted on randomly generated
`Erdos-Renyi <https://en.wikipedia.org/wiki/Erdos-Renyi_model>`__
graphs, commonly denoted by :math:`G(n,p)`. These graphs are constructed
by taking :math:`n` nodes and adding an edge between each node pair at
random with probability :math:`p`. The expected number of edges in a
:math:`G(n,p)` graph is therefore :math:`\binom{n}{2}p`, while the
expected node degree is :math:`(n-1)p`.

For these tests, we use differing values for :math:`n` but keep
:math:`p` fixed at :math:`0.5`. This is due to a
`result <https://mathoverflow.net/questions/424327/selection-of-an-n-node-graph-at-random>`__
of `Nick Wormald <https://en.wikipedia.org/wiki/Nick_Wormald>`__, who
has established that for :math:`n \gtrapprox 30`, a set of randomly
constructed :math:`G(n, 0.5)` graphs can be considered equivalent to a
random sample from the population of *all* :math:`n`-node graphs. Note,
however, that although this allows us to make general statistical
statements about performance, different observations may well be made
when executing these algorithms on specifically chosen topologies, such
as `scale-free
graphs <https://en.wikipedia.org/wiki/Scale-free_network>`__ and `planar
graphs <https://en.wikipedia.org/wiki/Planar_graph>`__. Examples of
these differences are discussed in this
`book <https://link.springer.com/book/10.1007/978-3-030-81054-2>`__.

In the code below, each trial involves generating a set of
:math:`G(n,0.5)` graphs using a range of values of :math:`n`. The
results of the algorithms are then written to a Pandas dataframe ``df``,
and this data is summarized in charts and pivot tables. Lines in the
charts give mean values, while the shaded areas indicate one standard
deviation on either side of these means. All results below were found by
executing the code on a 3.0 GHtz Windows 11 PC with 16 GB of RAM.

Differing Node Coloring Strategies
----------------------------------

In our first experiment, we compare the different constructive
strategies available for node coloring in the ``gcol`` library (namely
``'random'``, ``'welsh_powell'``, ``'dsatur'``, and ``'rlf'``) using
:math:`G(n,0.5)` graphs with values of :math:`n` between :math:`50` and
:math:`500`. The results are shown in the pivot table and charts below.
Further details on these algorithms can be found in ``gcol``\ ’s
documentation.

.. code:: ipython3

    import pandas as pd
    import networkx as nx
    import gcol
    import matplotlib.pyplot as plt
    import time
    
    #Carry out the trials and put the results into a list
    results = []
    nVals = range(50,501,50)
    for n in nVals:
        for seed in range(50):
            G = nx.gnp_random_graph(n, 0.5, seed)
            for strategy in ["random", "welsh_powell", "dsatur", "rlf"]:
                start = time.time()
                c = gcol.node_coloring(G, strategy)
                results.append([n, seed, strategy, max(c.values()) + 1, time.time()-start])
                
    # Create a pandas dataframe from this list, make a pivot table, and display it
    df = pd.DataFrame(results, columns=["n", "seed", "strategy", "cols", "time"])
    pivot = df.pivot_table(columns='strategy', aggfunc=['mean','std'], values=['cols','time'], index='n')
    display(pivot)



.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead tr th {
            text-align: left;
        }
    
        .dataframe thead tr:last-of-type th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr>
          <th></th>
          <th colspan="8" halign="left">mean</th>
          <th colspan="8" halign="left">std</th>
        </tr>
        <tr>
          <th></th>
          <th colspan="4" halign="left">cols</th>
          <th colspan="4" halign="left">time</th>
          <th colspan="4" halign="left">cols</th>
          <th colspan="4" halign="left">time</th>
        </tr>
        <tr>
          <th>strategy</th>
          <th>dsatur</th>
          <th>random</th>
          <th>rlf</th>
          <th>welsh_powell</th>
          <th>dsatur</th>
          <th>random</th>
          <th>rlf</th>
          <th>welsh_powell</th>
          <th>dsatur</th>
          <th>random</th>
          <th>rlf</th>
          <th>welsh_powell</th>
          <th>dsatur</th>
          <th>random</th>
          <th>rlf</th>
          <th>welsh_powell</th>
        </tr>
        <tr>
          <th>n</th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>50</th>
          <td>11.00</td>
          <td>12.90</td>
          <td>10.60</td>
          <td>12.02</td>
          <td>0.001126</td>
          <td>0.000334</td>
          <td>0.004669</td>
          <td>0.000021</td>
          <td>0.571429</td>
          <td>0.863075</td>
          <td>0.534522</td>
          <td>0.684821</td>
          <td>0.003808</td>
          <td>0.002212</td>
          <td>0.006797</td>
          <td>0.000141</td>
        </tr>
        <tr>
          <th>100</th>
          <td>18.20</td>
          <td>21.36</td>
          <td>17.24</td>
          <td>19.96</td>
          <td>0.003144</td>
          <td>0.000055</td>
          <td>0.031238</td>
          <td>0.000160</td>
          <td>0.571429</td>
          <td>0.875051</td>
          <td>0.591090</td>
          <td>0.698687</td>
          <td>0.004793</td>
          <td>0.000214</td>
          <td>0.004788</td>
          <td>0.000371</td>
        </tr>
        <tr>
          <th>150</th>
          <td>24.84</td>
          <td>28.78</td>
          <td>23.14</td>
          <td>27.04</td>
          <td>0.008169</td>
          <td>0.000625</td>
          <td>0.100434</td>
          <td>0.000352</td>
          <td>0.841767</td>
          <td>1.130107</td>
          <td>0.606428</td>
          <td>1.068281</td>
          <td>0.007916</td>
          <td>0.003092</td>
          <td>0.008025</td>
          <td>0.002212</td>
        </tr>
        <tr>
          <th>200</th>
          <td>30.96</td>
          <td>36.10</td>
          <td>28.96</td>
          <td>33.76</td>
          <td>0.014932</td>
          <td>0.000174</td>
          <td>0.238887</td>
          <td>0.001273</td>
          <td>0.727310</td>
          <td>1.281740</td>
          <td>0.698687</td>
          <td>0.938083</td>
          <td>0.013072</td>
          <td>0.001098</td>
          <td>0.007489</td>
          <td>0.004277</td>
        </tr>
        <tr>
          <th>250</th>
          <td>37.14</td>
          <td>42.56</td>
          <td>34.30</td>
          <td>40.08</td>
          <td>0.019173</td>
          <td>0.001935</td>
          <td>0.447659</td>
          <td>0.000433</td>
          <td>0.926041</td>
          <td>1.311799</td>
          <td>0.677631</td>
          <td>1.026983</td>
          <td>0.006828</td>
          <td>0.005113</td>
          <td>0.008536</td>
          <td>0.002245</td>
        </tr>
        <tr>
          <th>300</th>
          <td>42.72</td>
          <td>48.68</td>
          <td>39.56</td>
          <td>46.24</td>
          <td>0.030017</td>
          <td>0.002138</td>
          <td>0.786219</td>
          <td>0.001789</td>
          <td>1.195911</td>
          <td>1.096190</td>
          <td>0.674915</td>
          <td>1.021404</td>
          <td>0.017120</td>
          <td>0.004685</td>
          <td>0.013414</td>
          <td>0.004237</td>
        </tr>
        <tr>
          <th>350</th>
          <td>48.86</td>
          <td>54.94</td>
          <td>44.82</td>
          <td>52.36</td>
          <td>0.037244</td>
          <td>0.002165</td>
          <td>1.193058</td>
          <td>0.002740</td>
          <td>0.833238</td>
          <td>1.038248</td>
          <td>0.774333</td>
          <td>1.083456</td>
          <td>0.008014</td>
          <td>0.005124</td>
          <td>0.009833</td>
          <td>0.005731</td>
        </tr>
        <tr>
          <th>400</th>
          <td>54.38</td>
          <td>60.82</td>
          <td>50.08</td>
          <td>58.38</td>
          <td>0.047678</td>
          <td>0.005056</td>
          <td>1.773202</td>
          <td>0.003022</td>
          <td>0.923392</td>
          <td>1.063111</td>
          <td>0.633745</td>
          <td>1.066943</td>
          <td>0.003849</td>
          <td>0.007170</td>
          <td>0.011331</td>
          <td>0.006023</td>
        </tr>
        <tr>
          <th>450</th>
          <td>59.74</td>
          <td>66.70</td>
          <td>54.94</td>
          <td>64.12</td>
          <td>0.062071</td>
          <td>0.003636</td>
          <td>2.596551</td>
          <td>0.004267</td>
          <td>1.139459</td>
          <td>1.035098</td>
          <td>0.711710</td>
          <td>1.319245</td>
          <td>0.006253</td>
          <td>0.006539</td>
          <td>0.026104</td>
          <td>0.006861</td>
        </tr>
        <tr>
          <th>500</th>
          <td>65.08</td>
          <td>72.24</td>
          <td>60.06</td>
          <td>69.72</td>
          <td>0.075578</td>
          <td>0.006313</td>
          <td>3.614420</td>
          <td>0.005314</td>
          <td>0.965528</td>
          <td>1.450686</td>
          <td>0.711710</td>
          <td>1.178723</td>
          <td>0.006116</td>
          <td>0.007522</td>
          <td>0.035249</td>
          <td>0.007270</td>
        </tr>
      </tbody>
    </table>
    </div>


.. code:: ipython3

    # Now use the pivot table above to make a chart that compares mean solution quality
    mean1, SD1 = pivot[("mean","cols","random")], pivot[("std","cols","random")]
    mean2, SD2 = pivot[("mean","cols","welsh_powell")], pivot[("std","cols","welsh_powell")]
    mean3, SD3 = pivot[("mean","cols","dsatur")], pivot[("std","cols","dsatur")]
    mean4, SD4 = pivot[("mean","cols","rlf")], pivot[("std","cols","rlf")]
    plt.plot(nVals, mean1, linestyle='-', linewidth=1.5, color="b", label='Random')
    plt.fill_between(nVals, mean1-SD1, mean1+SD1, color='b', alpha=0.2)
    plt.plot(nVals, mean2, linestyle='--', linewidth=1.5, color="r", label='Welsh-Powell')
    plt.fill_between(nVals, mean2-SD2, mean2+SD2, color='r', alpha=0.2)
    plt.plot(nVals, mean3, linestyle='-.', linewidth=1.5, color="g", label='DSatur')
    plt.fill_between(nVals, mean3-SD3, mean3+SD3, color='k', alpha=0.2)
    plt.plot(nVals, mean4, linestyle=':', linewidth=1.5, color="black", label='RLF')
    plt.fill_between(nVals, mean4-SD4, mean4+SD4, color='g', alpha=0.2)
    plt.xlabel("Number of nodes $n$")
    plt.ylabel("Colours")
    plt.legend()
    plt.show()
    
    # and do the same for mean run times
    mean1, SD1 = pivot[("mean","time","random")], pivot[("std","time","random")]
    mean2, SD2 = pivot[("mean","time","welsh_powell")], pivot[("std","time","welsh_powell")]
    mean3, SD3 = pivot[("mean","time","dsatur")], pivot[("std","time","dsatur")]
    mean4, SD4 = pivot[("mean","time","rlf")], pivot[("std","time","rlf")]
    plt.plot(nVals, mean1, linestyle='-', linewidth=1.5, color="b", label='Random')
    plt.fill_between(nVals, mean1-SD1, mean1+SD1, color='b', alpha=0.2)
    plt.plot(nVals, mean2, linestyle='--', linewidth=1.5, color="r", label='Welsh-Powell')
    plt.fill_between(nVals, mean2-SD2, mean2+SD2, color='r', alpha=0.2)
    plt.plot(nVals, mean3, linestyle='-.', linewidth=1.5, color="g", label='DSatur')
    plt.fill_between(nVals, mean3-SD3, mean3+SD3, color='k', alpha=0.2)
    plt.plot(nVals, mean4, linestyle=':', linewidth=1.5, color="black", label='RLF')
    plt.fill_between(nVals, mean4-SD4, mean4+SD4, color='g', alpha=0.2)
    plt.xlabel("Number of nodes $n$")
    plt.ylabel("Run time (s)")
    plt.legend()
    plt.show()



.. image:: output_2_0.png



.. image:: output_2_1.png


The results above show that the ``random`` and ``welsh-powell``
strategies produce the poorest solutions overall (in terms of the number
of colors they use) while the RLF algorithm produces the best. This gap
also seems to widen for larger values of :math:`n`. On the other hand,
the RLF algorithm has less favorable run times, as shown in the second
chart. This is to be expected because the RLF algorithm has a higher
complexity than the others. A good compromise seems to be struck by the
``dsatur`` strategy, which features comparatively good solution quality
and run times.

Comparison to NetworkX
----------------------

The next set of experiments compares the performance of ``gcol``\ ’s
local search routines and NetworkX’s `interchange coloring
routine <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.coloring.greedy_color.html>`__.
As a benchmark, we also include ``gcol``\ ’s ``dsatur`` option from
earlier, which has also been used to produce the initial solutions for
the local search algorithms. For comparative purposes, both of
``gcol``\ ’s local search algorithms (``opt_alg=2`` and ``opt_alg=3``)
are used here, and we impose a fixed iteration limit of :math:`n`. The
results are collected and displayed in the same manner as the previous
example.

.. code:: ipython3

    #Carry out the trials and put the results into a list
    results = []
    nVals = range(50,601,50)
    for n in nVals:
        for seed in range(50):
            G = nx.gnp_random_graph(n, 0.5, seed)
            start = time.time()
            c = nx.greedy_color(G, "largest_first", interchange=True)
            results.append([n, seed, "networkx", max(c.values()) + 1, time.time()-start])
            start = time.time()
            c = gcol.node_coloring(G)
            results.append([n, seed, "dsatur", max(c.values()) + 1, time.time()-start])
            start = time.time()
            c = gcol.node_coloring(G, opt_alg=2, it_limit=len(G))
            results.append([n, seed, "opt_alg=2", max(c.values()) + 1, time.time()-start])
            start = time.time()
            c = gcol.node_coloring(G, opt_alg=3, it_limit=len(G))
            results.append([n, seed, "opt_alg=3", max(c.values()) + 1, time.time()-start])
                
    # Create a pandas dataframe from this list and make a pivot table
    df = pd.DataFrame(results, columns=["n", "seed", "alg", "cols", "time"])
    pivot = df.pivot_table(columns='alg', aggfunc=['mean','std'], values=['cols','time'], index='n')
    display(pivot)
    
    # Use the pivot table to make charts as before
    mean1, SD1 = pivot[("mean","cols","networkx")], pivot[("std","cols","networkx")]
    mean2, SD2 = pivot[("mean","cols","dsatur")], pivot[("std","cols","dsatur")]
    mean3, SD3 = pivot[("mean","cols","opt_alg=2")], pivot[("std","cols","opt_alg=2")]
    mean4, SD4 = pivot[("mean","cols","opt_alg=3")], pivot[("std","cols","opt_alg=3")]
    plt.plot(nVals, mean1, linestyle='-', linewidth=1.5, color="b", label='NetworkX')
    plt.fill_between(nVals, mean1-SD1, mean1+SD1, color='b', alpha=0.2)
    plt.plot(nVals, mean2, linestyle='--', linewidth=1.5, color="r", label='DSatur')
    plt.fill_between(nVals, mean2-SD2, mean2+SD2, color='r', alpha=0.2)
    plt.plot(nVals, mean3, linestyle='-.', linewidth=1.5, color="g", label='opt_alg=2')
    plt.fill_between(nVals, mean3-SD3, mean3+SD3, color='k', alpha=0.2)
    plt.plot(nVals, mean4, linestyle=':', linewidth=1.5, color="black", label='opt_alg=3')
    plt.fill_between(nVals, mean4-SD4, mean4+SD4, color='g', alpha=0.2)
    plt.xlabel("Number of nodes $n$")
    plt.ylabel("Colours")
    plt.legend()
    plt.show()
    
    mean1, SD1 = pivot[("mean","time","networkx")], pivot[("std","time","networkx")]
    mean2, SD2 = pivot[("mean","time","dsatur")], pivot[("std","time","dsatur")]
    mean3, SD3 = pivot[("mean","time","opt_alg=2")], pivot[("std","time","opt_alg=2")]
    mean4, SD4 = pivot[("mean","time","opt_alg=3")], pivot[("std","time","opt_alg=3")]
    plt.plot(nVals, mean1, linestyle='-', linewidth=1.5, color="b", label='NetworkX')
    plt.fill_between(nVals, mean1-SD1, mean1+SD1, color='b', alpha=0.2)
    plt.plot(nVals, mean2, linestyle='--', linewidth=1.5, color="r", label='DSatur')
    plt.fill_between(nVals, mean2-SD2, mean2+SD2, color='r', alpha=0.2)
    plt.plot(nVals, mean3, linestyle='-.', linewidth=1.5, color="g", label='opt_alg=2')
    plt.fill_between(nVals, mean3-SD3, mean3+SD3, color='k', alpha=0.2)
    plt.plot(nVals, mean4, linestyle=':', linewidth=1.5, color="black", label='opt_alg=3')
    plt.fill_between(nVals, mean4-SD4, mean4+SD4, color='g', alpha=0.2)
    plt.xlabel("Number of nodes $n$")
    plt.ylabel("Run time (s)")
    plt.legend()
    plt.show()



.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead tr th {
            text-align: left;
        }
    
        .dataframe thead tr:last-of-type th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr>
          <th></th>
          <th colspan="8" halign="left">mean</th>
          <th colspan="8" halign="left">std</th>
        </tr>
        <tr>
          <th></th>
          <th colspan="4" halign="left">cols</th>
          <th colspan="4" halign="left">time</th>
          <th colspan="4" halign="left">cols</th>
          <th colspan="4" halign="left">time</th>
        </tr>
        <tr>
          <th>alg</th>
          <th>dsatur</th>
          <th>networkx</th>
          <th>opt_alg=2</th>
          <th>opt_alg=3</th>
          <th>dsatur</th>
          <th>networkx</th>
          <th>opt_alg=2</th>
          <th>opt_alg=3</th>
          <th>dsatur</th>
          <th>networkx</th>
          <th>opt_alg=2</th>
          <th>opt_alg=3</th>
          <th>dsatur</th>
          <th>networkx</th>
          <th>opt_alg=2</th>
          <th>opt_alg=3</th>
        </tr>
        <tr>
          <th>n</th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>50</th>
          <td>11.00</td>
          <td>10.58</td>
          <td>10.24</td>
          <td>10.44</td>
          <td>0.001198</td>
          <td>0.002848</td>
          <td>0.004415</td>
          <td>0.004150</td>
          <td>0.571429</td>
          <td>0.609114</td>
          <td>0.476381</td>
          <td>0.611455</td>
          <td>0.003728</td>
          <td>0.005433</td>
          <td>0.005995</td>
          <td>0.005789</td>
        </tr>
        <tr>
          <th>100</th>
          <td>18.20</td>
          <td>17.72</td>
          <td>16.90</td>
          <td>17.10</td>
          <td>0.002699</td>
          <td>0.011782</td>
          <td>0.022187</td>
          <td>0.015837</td>
          <td>0.571429</td>
          <td>0.671277</td>
          <td>0.505076</td>
          <td>0.580288</td>
          <td>0.005744</td>
          <td>0.011038</td>
          <td>0.012093</td>
          <td>0.003045</td>
        </tr>
        <tr>
          <th>150</th>
          <td>24.84</td>
          <td>24.30</td>
          <td>23.04</td>
          <td>23.16</td>
          <td>0.012574</td>
          <td>0.032542</td>
          <td>0.047948</td>
          <td>0.039211</td>
          <td>0.841767</td>
          <td>0.646813</td>
          <td>0.668840</td>
          <td>0.680936</td>
          <td>0.012057</td>
          <td>0.013263</td>
          <td>0.015423</td>
          <td>0.007838</td>
        </tr>
        <tr>
          <th>200</th>
          <td>30.96</td>
          <td>30.52</td>
          <td>28.50</td>
          <td>28.94</td>
          <td>0.015713</td>
          <td>0.079482</td>
          <td>0.080056</td>
          <td>0.068262</td>
          <td>0.727310</td>
          <td>0.788696</td>
          <td>0.580288</td>
          <td>0.711710</td>
          <td>0.011063</td>
          <td>0.023787</td>
          <td>0.009535</td>
          <td>0.009321</td>
        </tr>
        <tr>
          <th>250</th>
          <td>37.14</td>
          <td>36.46</td>
          <td>34.30</td>
          <td>34.42</td>
          <td>0.024954</td>
          <td>0.139182</td>
          <td>0.129421</td>
          <td>0.109929</td>
          <td>0.926041</td>
          <td>0.885484</td>
          <td>0.646813</td>
          <td>0.609114</td>
          <td>0.018215</td>
          <td>0.029630</td>
          <td>0.013072</td>
          <td>0.008136</td>
        </tr>
        <tr>
          <th>300</th>
          <td>42.72</td>
          <td>42.00</td>
          <td>39.46</td>
          <td>39.84</td>
          <td>0.034277</td>
          <td>0.233811</td>
          <td>0.192308</td>
          <td>0.164115</td>
          <td>1.195911</td>
          <td>0.755929</td>
          <td>0.705951</td>
          <td>0.680936</td>
          <td>0.020489</td>
          <td>0.029099</td>
          <td>0.010850</td>
          <td>0.010551</td>
        </tr>
        <tr>
          <th>350</th>
          <td>48.86</td>
          <td>47.98</td>
          <td>44.62</td>
          <td>45.12</td>
          <td>0.036986</td>
          <td>0.366410</td>
          <td>0.276068</td>
          <td>0.232763</td>
          <td>0.833238</td>
          <td>0.769044</td>
          <td>0.602376</td>
          <td>0.479796</td>
          <td>0.007532</td>
          <td>0.024408</td>
          <td>0.018478</td>
          <td>0.011266</td>
        </tr>
        <tr>
          <th>400</th>
          <td>54.38</td>
          <td>53.46</td>
          <td>49.82</td>
          <td>50.16</td>
          <td>0.064390</td>
          <td>0.511017</td>
          <td>0.372623</td>
          <td>0.309454</td>
          <td>0.923392</td>
          <td>0.973317</td>
          <td>0.719694</td>
          <td>0.618095</td>
          <td>0.026725</td>
          <td>0.031725</td>
          <td>0.026486</td>
          <td>0.016676</td>
        </tr>
        <tr>
          <th>450</th>
          <td>59.74</td>
          <td>58.98</td>
          <td>55.00</td>
          <td>55.40</td>
          <td>0.089714</td>
          <td>0.686402</td>
          <td>0.470342</td>
          <td>0.400221</td>
          <td>1.139459</td>
          <td>0.769044</td>
          <td>0.728431</td>
          <td>0.808122</td>
          <td>0.033389</td>
          <td>0.049046</td>
          <td>0.028102</td>
          <td>0.020487</td>
        </tr>
        <tr>
          <th>500</th>
          <td>65.08</td>
          <td>64.46</td>
          <td>59.68</td>
          <td>60.24</td>
          <td>0.146833</td>
          <td>0.910533</td>
          <td>0.616006</td>
          <td>0.522832</td>
          <td>0.965528</td>
          <td>1.034309</td>
          <td>0.683329</td>
          <td>0.624663</td>
          <td>0.007637</td>
          <td>0.058123</td>
          <td>0.025956</td>
          <td>0.022833</td>
        </tr>
        <tr>
          <th>550</th>
          <td>70.44</td>
          <td>69.76</td>
          <td>64.68</td>
          <td>65.22</td>
          <td>0.133141</td>
          <td>1.241486</td>
          <td>0.799239</td>
          <td>0.676384</td>
          <td>0.951047</td>
          <td>0.959592</td>
          <td>0.712569</td>
          <td>0.708260</td>
          <td>0.042047</td>
          <td>0.076402</td>
          <td>0.034881</td>
          <td>0.026771</td>
        </tr>
        <tr>
          <th>600</th>
          <td>75.72</td>
          <td>74.68</td>
          <td>69.36</td>
          <td>69.98</td>
          <td>0.127430</td>
          <td>1.621527</td>
          <td>1.015307</td>
          <td>0.850793</td>
          <td>1.161280</td>
          <td>1.096190</td>
          <td>0.776176</td>
          <td>0.684821</td>
          <td>0.037837</td>
          <td>0.112966</td>
          <td>0.045676</td>
          <td>0.035609</td>
        </tr>
      </tbody>
    </table>
    </div>



.. image:: output_4_1.png



.. image:: output_4_2.png


It is clear from the above results that the local search algorithms make
significant improvements to the solutions provided by the ``dsatur``
strategy, albeit with additional time requirements. The solutions and
run times of these local search algorithms are also superior to
NetworkX’s node coloring routines. Note that further improvements in
solution quality might also be found by increasing the iteration limit
of the local search algorithms.

Exact Algorithm Performance
---------------------------

In addition to two local search heuristics, the ``gcol`` library also
features an exact, exponential-time algorithm for node coloring, based
on backtracking. This algorithm is invoked by setting ``opt_alg=1``. At
the start of this algorithm’s execution, a large clique :math:`C` is
identified in :math:`G` using the NetworkX function ``nx.max_clique()``.
The nodes of :math:`C` are then permanently assigned to different
colors. The main backtracking algorithm is then executed and only halts
only when a solution using :math:`C` colors has been identified, or when
the algorithm has backtracked to the root of the search tree. In both
cases the returned solution will be optimal (that is, will be using the
minimum number of colors).

The following code evaluates the performance of this algorithm on
:math:`G(n,0.5)` graphs for a range of :math:`n`-values.

.. code:: ipython3

    results = []
    nVals = range(2,55,2)
    for n in nVals:
        for seed in range(25):
            G = nx.gnp_random_graph(n, 0.5, seed)
            start = time.time()
            c = gcol.node_coloring(G, opt_alg=1)
            results.append([n, seed, "opt_alg=1", max(c.values()) + 1, time.time()-start])
            
    # Create a pandas datafram from this list and make a pivot 
    df = pd.DataFrame(results, columns=["n", "seed", "alg", "cols", "time"])
    pivot = df.pivot_table(columns='alg', aggfunc=['mean','std'], values=['cols','time'], index='n')
    
    # Use the pivot table above to make the charts as before
    mean1, SD1 = pivot[("mean","cols","opt_alg=1")], pivot[("std","cols","opt_alg=1")]
    plt.plot(nVals, mean1, linestyle='-', linewidth=1.5, color="b", label='opt_alg=1')
    plt.fill_between(nVals, mean1-SD1, mean1+SD1, color='b', alpha=0.2)
    plt.xlabel("Number of nodes $n$")
    plt.ylabel("Colours")
    plt.legend()
    plt.show()
    
    mean1, SD1 = pivot[("mean","time","opt_alg=1")], pivot[("std","time","opt_alg=1")]
    plt.plot(nVals, mean1, linestyle='-', linewidth=1.5, color="b", label='opt_alg=1')
    plt.fill_between(nVals, mean1-SD1, mean1+SD1, color='b', alpha=0.2)
    plt.xlabel("Number of nodes $n$")
    plt.ylim((0, 600))
    plt.ylabel("Run time (s)")
    plt.legend()
    plt.show()



.. image:: output_6_0.png



.. image:: output_6_1.png


The first chart above shows the chromatic numbers from a sample of
:math:`G(n,0.5)` graphs for an increasing number of nodes :math:`n`. It
can be seen that the chromatic number rises in a close-to-linear fashion
in relation to :math:`n`. The second figure also demonstrates the
disadvantages of using an exponential-time algorithm: once :math:`n` is
increased beyond a moderately small value (approximately 50 here), run
times become too high and/or unpredictable for practical use. Note,
however, that the specific :math:`n`-values that give in these
infeasible run times can vary considerably depending on the topology of
the graph. For example, planar graphs and scale-free graphs can often be
solved very quickly for graphs with several hundred nodes. These sorts
of results will usually need to be confirmed empirically.

Equitable Coloring
------------------

In the equitable node-coloring problem, we are interested in coloring
the nodes with a user-defined number of colors :math:`k` so that (a)
adjacent nodes have different colors, and (b) the number of nodes in
each color is as equal as possible. The following trials run the
``gcol.equitable_node_k_coloring()`` method on a sample of random
:math:`G(500,0.5)` graphs over a range of suitable :math:`k`-values. The
reported cost is simply the difference in size between the largest and
smallest color classes in a solution. Hence, if :math:`k` is a divisor
of :math:`n`, a cost of zero indicates an equitable :math:`k`-coloring,
else a cost of one indicates an equitable coloring.

.. code:: ipython3

    results = []
    n = 500
    kVals = range(70, 300, 1)
    for seed in range(50):
        G = nx.gnp_random_graph(n, 0.5, seed)
        for k in kVals:
            start = time.time()
            c = gcol.equitable_node_k_coloring(G, k, opt_alg=2, it_limit=len(G))
            P = gcol.partition(c)
            cost = max(len(j) for j in P) - min(len(j) for j in P)
            results.append([k, seed, "opt_alg=2", cost, time.time()-start])
    
    # Create a pandas dataframe from this list and make a pivot table
    df = pd.DataFrame(results, columns=["k", "seed", "alg", "cost", "time"])
    pivot = df.pivot_table(columns='alg', aggfunc=['mean','std'], values=['cost','time'], index='k')
    display(pivot)
    
    # Use the pivot table above to make charts as before
    mean1, SD1 = pivot[("mean","cost","opt_alg=2")], pivot[("std","cost","opt_alg=2")]
    plt.plot(kVals, mean1, linestyle='-', linewidth=1.5, color="b", label='opt_alg=2')
    plt.fill_between(kVals, mean1-SD1, mean1+SD1, color='b', alpha=0.2)
    plt.xlabel("Number of colors $k$")
    plt.ylabel("Cost")
    plt.legend()
    plt.show()
    
    mean1, SD1 = pivot[("mean","time","opt_alg=2")], pivot[("std","time","opt_alg=2")]
    plt.plot(kVals, mean1, linestyle='-', linewidth=1.5, color="b", label='opt_alg=2')
    plt.fill_between(kVals, mean1-SD1, mean1+SD1, color='b', alpha=0.2)
    plt.xlabel("Number of colors $k$")
    plt.ylabel("Run time (s)")
    plt.legend()
    plt.show()



.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead tr th {
            text-align: left;
        }
    
        .dataframe thead tr:last-of-type th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr>
          <th></th>
          <th colspan="2" halign="left">mean</th>
          <th colspan="2" halign="left">std</th>
        </tr>
        <tr>
          <th></th>
          <th>cost</th>
          <th>time</th>
          <th>cost</th>
          <th>time</th>
        </tr>
        <tr>
          <th>alg</th>
          <th>opt_alg=2</th>
          <th>opt_alg=2</th>
          <th>opt_alg=2</th>
          <th>opt_alg=2</th>
        </tr>
        <tr>
          <th>k</th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>70</th>
          <td>2.06</td>
          <td>1.392196</td>
          <td>0.313636</td>
          <td>1.191423</td>
        </tr>
        <tr>
          <th>71</th>
          <td>2.02</td>
          <td>1.315562</td>
          <td>0.141421</td>
          <td>1.189239</td>
        </tr>
        <tr>
          <th>72</th>
          <td>2.00</td>
          <td>0.930378</td>
          <td>0.000000</td>
          <td>0.755660</td>
        </tr>
        <tr>
          <th>73</th>
          <td>1.86</td>
          <td>0.844038</td>
          <td>0.350510</td>
          <td>0.565452</td>
        </tr>
        <tr>
          <th>74</th>
          <td>1.52</td>
          <td>0.650470</td>
          <td>0.504672</td>
          <td>0.117768</td>
        </tr>
        <tr>
          <th>...</th>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <th>295</th>
          <td>1.00</td>
          <td>3.110134</td>
          <td>0.000000</td>
          <td>0.037128</td>
        </tr>
        <tr>
          <th>296</th>
          <td>1.00</td>
          <td>3.130134</td>
          <td>0.000000</td>
          <td>0.032748</td>
        </tr>
        <tr>
          <th>297</th>
          <td>1.00</td>
          <td>3.153672</td>
          <td>0.000000</td>
          <td>0.038234</td>
        </tr>
        <tr>
          <th>298</th>
          <td>1.00</td>
          <td>3.182735</td>
          <td>0.000000</td>
          <td>0.038982</td>
        </tr>
        <tr>
          <th>299</th>
          <td>1.00</td>
          <td>3.199719</td>
          <td>0.000000</td>
          <td>0.040702</td>
        </tr>
      </tbody>
    </table>
    <p>230 rows × 4 columns</p>
    </div>



.. image:: output_8_1.png



.. image:: output_8_2.png


The first chart above demonstrates that the
``gcol.equitable_node_k_coloring()`` method consistently achieves
equitable node :math:`k`-colorings. The exceptions occur for low values
of :math:`k` (which are close to the chromatic number) and when
:math:`k` is a divisor of :math:`n`. In the former case, the low number
of available colors restricts the choice of appropriate colors for each
node, often leading to inequitable colorings. On the other hand, when
:math:`k` is a divisor of :math:`n`, the algorithm is seeking a solution
with a cost of zero, meaning that each color class must have *exactly*
the same number of nodes. If this cannot be done, then a cost of at
least two must be incurred.

The second chart above also indicates that runtimes of this routine
increase slightly when :math:`k` is a divisor of :math:`n`. Run times
also lengthen due to increases in :math:`k`. The latter is due to the
larger number of solutions that need to be evaluated in each iteration
of the local search algorithm used with this routine. More details on
this algorithm can be found in ``gcol``\ ’s documentation.

Finally, note that NetworkX also
`features <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.coloring.equitable_color.html>`__
an equitable node :math:`k`-coloring routine, but this can only be used
when :math:`k\geq \Delta(G)`, where :math:`\Delta(G)` is the highest
node degree in the graph. In the :math:`G(500,0.5)` graphs considered
here, the minimum valid value for :math:`k` is approximately 280.

Independent Set Comparison
--------------------------

Our final set or trials looks at the performance the
``gcol.max_independent_set()`` routine and compares it to the
`approximation
algorithm <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.approximation.clique.maximum_independent_set.html>`__
included in NetworkX for the same problem. As before, we use an
iteration limit of :math:`n` for the former.

.. code:: ipython3

    #Carry out the trials and put the results into a list
    results = []
    nVals = range(50,501,50)
    for n in nVals:
        for seed in range(50):
            G = nx.gnp_random_graph(n, 0.5, seed)
            start = time.time()
            S = gcol.max_independent_set(G, it_limit=len(G))
            results.append([n, seed, "gcol", len(S), time.time()-start])
            start = time.time()
            S = nx.approximation.maximum_independent_set(G)
            results.append([n, seed, "networkx", len(S), time.time()-start])
            
    # Create a pandas dataframe from this list and make a pivot table
    df = pd.DataFrame(results, columns=["n", "seed", "alg", "size", "time"])
    pivot = df.pivot_table(columns='alg', aggfunc=['mean','std'], values=['size','time'], index='n')
    display(pivot)
    
    # Create the charts as before
    mean1, SD1 = pivot[("mean","size","networkx")], pivot[("std","size","networkx")]
    mean2, SD2 = pivot[("mean","size","gcol")], pivot[("std","size","gcol")]
    plt.plot(nVals, mean1, linestyle='-', linewidth=1.5, color="b", label='NetworkX')
    plt.fill_between(nVals, mean1-SD1, mean1+SD1, color='b', alpha=0.2)
    plt.plot(nVals, mean2, linestyle='--', linewidth=1.5, color="r", label='GCol')
    plt.fill_between(nVals, mean2-SD2, mean2+SD2, color='r', alpha=0.2)
    plt.xlabel("Number of nodes $n$")
    plt.ylabel("Independent Set Size")
    plt.legend()
    plt.show()
    
    mean1, SD1 = pivot[("mean","time","networkx")], pivot[("std","time","networkx")]
    mean2, SD2 = pivot[("mean","time","gcol")], pivot[("std","time","gcol")]
    plt.plot(nVals, mean1, linestyle='-', linewidth=1.5, color="b", label='NetworkX')
    plt.fill_between(nVals, mean1-SD1, mean1+SD1, color='b', alpha=0.2)
    plt.plot(nVals, mean2, linestyle='--', linewidth=1.5, color="r", label='GCol')
    plt.fill_between(nVals, mean2-SD2, mean2+SD2, color='r', alpha=0.2)
    plt.xlabel("Number of nodes $n$")
    plt.ylabel("Run time (s)")
    plt.legend()
    plt.show()        



.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead tr th {
            text-align: left;
        }
    
        .dataframe thead tr:last-of-type th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr>
          <th></th>
          <th colspan="4" halign="left">mean</th>
          <th colspan="4" halign="left">std</th>
        </tr>
        <tr>
          <th></th>
          <th colspan="2" halign="left">size</th>
          <th colspan="2" halign="left">time</th>
          <th colspan="2" halign="left">size</th>
          <th colspan="2" halign="left">time</th>
        </tr>
        <tr>
          <th>alg</th>
          <th>gcol</th>
          <th>networkx</th>
          <th>gcol</th>
          <th>networkx</th>
          <th>gcol</th>
          <th>networkx</th>
          <th>gcol</th>
          <th>networkx</th>
        </tr>
        <tr>
          <th>n</th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>50</th>
          <td>7.26</td>
          <td>6.18</td>
          <td>0.001903</td>
          <td>0.012434</td>
          <td>0.443087</td>
          <td>0.522553</td>
          <td>0.004685</td>
          <td>0.006328</td>
        </tr>
        <tr>
          <th>100</th>
          <td>8.66</td>
          <td>7.46</td>
          <td>0.005674</td>
          <td>0.059977</td>
          <td>0.626295</td>
          <td>0.542481</td>
          <td>0.007545</td>
          <td>0.005775</td>
        </tr>
        <tr>
          <th>150</th>
          <td>9.46</td>
          <td>8.08</td>
          <td>0.015010</td>
          <td>0.159122</td>
          <td>0.503457</td>
          <td>0.633745</td>
          <td>0.003096</td>
          <td>0.011683</td>
        </tr>
        <tr>
          <th>200</th>
          <td>10.22</td>
          <td>8.58</td>
          <td>0.024277</td>
          <td>0.327061</td>
          <td>0.545482</td>
          <td>0.498569</td>
          <td>0.007783</td>
          <td>0.011075</td>
        </tr>
        <tr>
          <th>250</th>
          <td>10.58</td>
          <td>8.92</td>
          <td>0.041264</td>
          <td>0.572276</td>
          <td>0.574634</td>
          <td>0.488229</td>
          <td>0.007566</td>
          <td>0.027020</td>
        </tr>
        <tr>
          <th>300</th>
          <td>10.96</td>
          <td>9.28</td>
          <td>0.060024</td>
          <td>0.929584</td>
          <td>0.493219</td>
          <td>0.453557</td>
          <td>0.007967</td>
          <td>0.020480</td>
        </tr>
        <tr>
          <th>350</th>
          <td>11.18</td>
          <td>9.68</td>
          <td>0.080014</td>
          <td>1.398700</td>
          <td>0.437526</td>
          <td>0.586933</td>
          <td>0.007499</td>
          <td>0.023576</td>
        </tr>
        <tr>
          <th>400</th>
          <td>11.52</td>
          <td>9.86</td>
          <td>0.104997</td>
          <td>1.991064</td>
          <td>0.543609</td>
          <td>0.452205</td>
          <td>0.007658</td>
          <td>0.036276</td>
        </tr>
        <tr>
          <th>450</th>
          <td>11.70</td>
          <td>10.18</td>
          <td>0.131589</td>
          <td>2.724932</td>
          <td>0.543984</td>
          <td>0.522553</td>
          <td>0.007824</td>
          <td>0.048998</td>
        </tr>
        <tr>
          <th>500</th>
          <td>12.00</td>
          <td>10.38</td>
          <td>0.161875</td>
          <td>3.609545</td>
          <td>0.494872</td>
          <td>0.530306</td>
          <td>0.007575</td>
          <td>0.040481</td>
        </tr>
      </tbody>
    </table>
    </div>



.. image:: output_10_1.png



.. image:: output_10_2.png


The results above show clearly that the ``gcol.max_independent_set()``
routine produces larger independent sets (and therefore better quality
solutions) in less run time. As before, further improvements in solution
quality (but longer run times) may also be found by increasing the
``it_limit`` parameter.

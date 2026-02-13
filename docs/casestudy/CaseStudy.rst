Case Study: Exam Timetabling
============================

In this chapter, we consider a practical case study concerning the use
of graph coloring methods in the production of exam timetables at a
university. This will help to showcase the various tools available in
the ``gcol`` library.

Background
----------

Each year, a college needs to produce an exam timetable for its
students. The aim is to assign each exam to a “timeslot” while trying to
avoid “clashes”. (A clash occurs when there are one or more students who
need to attend a pair of exams, but these exams have been assigned to
the same timeslot and therefore occur at the same time.)

The problem is specified using an :math:`n\times n` symmetrical matrix
:math:`X`, where :math:`n` is the number of exams to schedule. An
element :math:`X_{ij}` in this matrix gives the number of students who
need to sit both exams :math:`i` and :math:`j`. Also, an element
:math:`X_{ii}` gives the total number of students sitting exam
:math:`i`. For example, in the following matrix:

.. math::


   \begin{pmatrix}
   9 & 0 & 0 & 1 & 0 & 0 & 6 & 0 \\
   0 & 4 & 0 & 0 & 0 & 0 & 0 & 1 \\
   0 & 0 & 9 & 0 & 4 & 0 & 0 & 0 \\
   1 & 0 & 0 & 3 & 0 & 0 & 0 & 1 \\
   0 & 0 & 4 & 0 & 8 & 0 & 0 & 3 \\
   0 & 0 & 0 & 0 & 0 & 4 & 0 & 0 \\
   6 & 0 & 0 & 0 & 0 & 0 & 9 & 2 \\
   0 & 1 & 0 & 1 & 3 & 0 & 2 & 8
   \end{pmatrix}

- There are :math:`n=8` exams (labelled 0 to 7),
- There is one student who needs to sit exams 0 and 3 (because
  :math:`X_{0,3}=1`),
- There are six students who need to sit exams 0 and 7 (because
  :math:`X_{0,7}=6`),
- Nine students are sitting exam 0 (because :math:`X_{0,0}=9`), and so
  on.

In this matrix, zeros indicate that no students need to sit the two
corresponding exams. This means that the pair of exams can be assigned
to the same timeslot, and no students will be inconvenienced.

A college administrator has been put in charge of creating this year’s
timetable, which involves :math:`n=139` exams. The full details of this
problem are given to her in the file
`timetable.txt <https://github.com/Rhyd-Lewis/GCol/blob/main/docs/casestudy/timetable.txt>`__,
which contains an :math:`n \times n` symmetrical matrix as described
above. She quickly realizes that this problem is too large to solve by
hand but can be handled using graph coloring techniques, using nodes for
exams and colors for timeslots.

An Initial Solution
-------------------

To start, our administrator reads the file
`timetable.txt <https://github.com/Rhyd-Lewis/GCol/blob/main/docs/casestudy/timetable.txt>`__
into a matrix :math:`X` and creates an :math:`n`-node graph where each
node corresponds to an exam. Nodes in this graph are then made adjacent
whenever the corresponding pair of exams has a common student. That is,
nodes :math:`v_i` and :math:`v_j` are made adjacent if and only if
:math:`X_{ij}>0` and :math:`i\neq j`. Having done this, the
administrator determines the chromatic number of this graph. This
corresponds to the minimum number of timeslots that are needed to
construct a clash-free timetable.

.. code:: ipython3

    import networkx as nx
    import gcol
    import matplotlib.pyplot as plt
    
    #Read in the text file and store in matrix X
    X = []
    with open('timetable.txt','r') as f:
        n = int(f.readline())
        for i in range(n):
            line = f.readline().split(",")
            line = [int(x) for x in line]
            X.append(line)
    
    #Construct the graph G
    G = nx.Graph()
    G.add_nodes_from([i for i in range(n) if X[i][i] > 0])
    for i in range(n-1):
        for j in range(i+1, n):
            if X[i][j] > 0:
                G.add_edge(i, j)
    print("Constructed a", G)
    print("Minimum number of timeslots needed for a clash free timetable =", gcol.chromatic_number(G))


.. parsed-literal::

    Constructed a Graph with 139 nodes and 1381 edges
    Minimum number of timeslots needed for a clash free timetable = 13
    

The results reveal that clash-free timetables are only possible when 13
or more timeslots are used to schedule these exams.

Scheduling Large Exams First
----------------------------

In previous years, the college has constructed the timetable by taking
the largest 15 exams and assigning each one to a different timeslot. The
remaining exams are then added to the timetable, creating new timeslots
where needed. The administrator thinks this could be a way forward and
uses ``gcol``\ ’s precoloring routines to emulate this process.

.. code:: ipython3

    #Get a list of exams, sorted by size, and assign the first 15 to different colors
    sizeExam = [(X[i][i], i) for i in range(n)]
    sizeExam.sort(reverse=True)
    print("Here are the sizes of each exam")
    print(sizeExam)
    
    P = {}
    for i in range(15):
        print("Exam", sizeExam[i][1], "has", sizeExam[i][0], "students. Assigning to timeslot", i)
        P[sizeExam[i][1]] = i
    
    c = gcol.node_precoloring(G, P, opt_alg=1)
    P = gcol.partition(c)
    print("Here are the exams assigned to each timeslot")
    for i in range(len(P)):
        print("Timeslot", i, ":", P[i])


.. parsed-literal::

    Here are the sizes of each exam
    [(236, 71), (208, 137), (208, 134), (208, 96), (208, 70), (208, 2), (127, 107), (121, 5), (119, 109), (118, 105), (117, 73), (110, 106), (101, 68), (90, 28), (89, 132), (89, 104), (87, 103), (84, 3), (77, 135), (74, 133), (73, 102), (71, 131), (67, 48), (61, 138), (39, 26), (35, 129), (35, 97), (34, 128), (34, 127), (34, 93), (34, 92), (34, 66), (34, 65), (34, 46), (34, 45), (34, 25), (34, 24), (33, 69), (32, 126), (32, 121), (32, 94), (32, 91), (32, 86), (32, 64), (32, 59), (32, 44), (32, 39), (32, 23), (32, 18), (31, 99), (30, 111), (30, 98), (30, 76), (30, 49), (30, 29), (30, 8), (29, 120), (29, 113), (29, 100), (29, 85), (29, 78), (29, 58), (29, 51), (29, 38), (29, 31), (29, 17), (29, 10), (28, 136), (28, 118), (28, 117), (28, 115), (28, 83), (28, 82), (28, 80), (28, 56), (28, 55), (28, 53), (28, 36), (28, 35), (28, 33), (28, 15), (28, 14), (28, 12), (27, 110), (27, 101), (27, 74), (27, 6), (26, 112), (26, 77), (26, 50), (26, 30), (26, 9), (24, 116), (24, 81), (24, 54), (24, 34), (24, 13), (23, 1), (21, 95), (20, 122), (20, 87), (20, 60), (20, 40), (20, 19), (19, 125), (19, 124), (19, 90), (19, 89), (19, 63), (19, 62), (19, 43), (19, 42), (19, 22), (19, 21), (13, 108), (12, 67), (12, 0), (10, 123), (10, 88), (10, 61), (10, 41), (10, 20), (9, 114), (9, 79), (9, 52), (9, 32), (9, 11), (8, 7), (7, 75), (7, 72), (2, 4), (1, 47), (0, 130), (0, 119), (0, 84), (0, 57), (0, 37), (0, 27), (0, 16)]
    Exam 71 has 236 students. Assigning to timeslot 0
    Exam 137 has 208 students. Assigning to timeslot 1
    Exam 134 has 208 students. Assigning to timeslot 2
    Exam 96 has 208 students. Assigning to timeslot 3
    Exam 70 has 208 students. Assigning to timeslot 4
    Exam 2 has 208 students. Assigning to timeslot 5
    Exam 107 has 127 students. Assigning to timeslot 6
    Exam 5 has 121 students. Assigning to timeslot 7
    Exam 109 has 119 students. Assigning to timeslot 8
    Exam 105 has 118 students. Assigning to timeslot 9
    Exam 73 has 117 students. Assigning to timeslot 10
    Exam 106 has 110 students. Assigning to timeslot 11
    Exam 68 has 101 students. Assigning to timeslot 12
    Exam 28 has 90 students. Assigning to timeslot 13
    Exam 132 has 89 students. Assigning to timeslot 14
    Here are the exams assigned to each timeslot
    Timeslot 0 : [9, 10, 29, 53, 71, 114, 116, 117, 118, 133]
    Timeslot 1 : [42, 43, 75, 86, 87, 91, 120, 123, 127, 128, 129, 137]
    Timeslot 2 : [26, 27, 84, 88, 94, 95, 99, 134]
    Timeslot 3 : [96]
    Timeslot 4 : [7, 61, 70, 72, 74, 85, 92, 93, 121, 122, 124, 125, 126]
    Timeslot 5 : [2, 57, 102, 103, 138]
    Timeslot 6 : [79, 81, 82, 83, 107, 111, 112, 113, 115, 130, 136]
    Timeslot 7 : [5, 6, 20, 38, 39, 40, 44, 45, 46, 62, 63]
    Timeslot 8 : [32, 33, 34, 35, 36, 37, 49, 50, 51, 97, 98, 100, 101, 108, 109, 110]
    Timeslot 9 : [47, 104, 105, 131, 135]
    Timeslot 10 : [41, 58, 59, 60, 64, 65, 66, 73, 89, 90]
    Timeslot 11 : [0, 1, 8, 11, 12, 13, 14, 15, 16, 30, 31, 106]
    Timeslot 12 : [3, 4, 52, 54, 55, 56, 67, 68, 69, 76, 77, 78, 80, 119]
    Timeslot 13 : [17, 18, 19, 21, 22, 23, 24, 25, 28]
    Timeslot 14 : [48, 132]
    

Balancing Exams
---------------

Despite the previous approach working satisfactorily, the administrator
decides that it is overly complex and abandons it. She also notices that
the seven smallest exams in the dataset have no attending students, so
she decides to remove them from the graph in future calculations. She is
also worried that some timeslots might contain too many exams and that
the university will not have enough seats available in these cases. As a
result, she decides to try and balance the number of students sitting
exams in each timeslot.

To do this, she creates a similar graph as above but specifies a weight
for each node, which gives the size of the corresponding exam. She also
ignores the seven empty exams. As shown, she is now able to produce a
clash-free 13-timeslot solution in which the number of students per
timeslot ranges between 417 and 443.

.. code:: ipython3

    #Construct the node-weighted graph G
    G = nx.Graph()
    for i in range(n):
        if X[i][i] > 0:
            G.add_node(i, weight=X[i][i])
    for i in range(n-1):
        for j in range(i+1, n):
            if X[i][i] > 0 and X[j][j] > 0 and X[i][j] > 0:
                G.add_edge(i, j)
    
    c = gcol.equitable_node_k_coloring(G, 13, weight="weight")
    P = gcol.partition(c)
    print("Here are the exams assigned to each timeslot")
    for i in range(len(P)):
        print("Timeslot", i, ":", P[i])
    for j in range(len(P)):
        Wj = [G.nodes[v]["weight"] for v in P[j]]
        print("Number of students in timeslot", j, "=", sum(Wj))


.. parsed-literal::

    Here are the exams assigned to each timeslot
    Timeslot 0 : [3, 72, 73, 74, 134]
    Timeslot 1 : [0, 1, 8, 13, 14, 17, 18, 19, 21, 22, 23, 24, 25, 33, 41, 51, 56]
    Timeslot 2 : [67, 68, 69, 104, 105, 132]
    Timeslot 3 : [5, 6, 7, 96, 135]
    Timeslot 4 : [20, 26, 70, 102, 103]
    Timeslot 5 : [12, 32, 47, 75, 78, 106, 107, 111, 117, 118, 129]
    Timeslot 6 : [2, 108, 109, 110, 138]
    Timeslot 7 : [4, 28, 97, 98, 100, 101, 137]
    Timeslot 8 : [9, 11, 15, 29, 35, 71, 133]
    Timeslot 9 : [36, 38, 39, 40, 42, 43, 44, 45, 46, 53, 79, 82, 112, 116, 131]
    Timeslot 10 : [10, 52, 58, 59, 60, 62, 63, 64, 65, 66, 76, 77, 80, 81, 83, 88, 136]
    Timeslot 11 : [30, 31, 48, 54, 55, 61, 85, 86, 87, 89, 90, 91, 92, 93, 115]
    Timeslot 12 : [34, 49, 50, 94, 95, 99, 113, 114, 120, 121, 122, 123, 124, 125, 126, 127, 128]
    Number of students in timeslot 0 = 443
    Number of students in timeslot 1 = 431
    Number of students in timeslot 2 = 442
    Number of students in timeslot 3 = 441
    Number of students in timeslot 4 = 417
    Number of students in timeslot 5 = 432
    Number of students in timeslot 6 = 428
    Number of students in timeslot 7 = 421
    Number of students in timeslot 8 = 431
    Number of students in timeslot 9 = 433
    Number of students in timeslot 10 = 431
    Number of students in timeslot 11 = 431
    Number of students in timeslot 12 = 431
    

Limiting Timeslots
------------------

At this point, the administrator is feeling rather pleased with herself:
she has produced a 13-timeslot solution, proved that this is the minimum
number of timeslots needed, and found a nice balance of students per
timeslot. She is somewhat irritated, then, when the college manager
tells her that there is ample seating capacity, but only twelve
timeslots. The latter means that the timetable will either need to have
some clashes or some unscheduled exams.

To investigate this, she first constructs a solution that seeks to
minimize the total size of unscheduled exams. To do this, she uses the
same node-weighted graph as above but makes use of the
``gcol.min_cost_k_coloring()`` routine. This leads to the following
solution:

.. code:: ipython3

    c = gcol.min_cost_k_coloring(G, 12, weight="weight", weights_at="nodes", it_limit=10000)
    P = gcol.partition(c)
    U = list(u for u in c if c[u] <= -1)
    print("Here are the exams assigned to each timeslot")
    for i in range(len(P)):
        print("Timeslot", i, ":", P[i])
    print("The unscheduled exams are", U)
    print("They have the following sizes", [G.nodes[u]["weight"] for u in U])


.. parsed-literal::

    Here are the exams assigned to each timeslot
    Timeslot 0 : [2, 3, 133]
    Timeslot 1 : [70, 71, 136]
    Timeslot 2 : [96, 102, 103, 132]
    Timeslot 3 : [47, 131, 134, 135]
    Timeslot 4 : [0, 1, 137, 138]
    Timeslot 5 : [94, 95, 99, 104, 105, 106, 107]
    Timeslot 6 : [4, 8, 9, 10, 11, 12, 13, 14, 15, 20, 26, 28, 48]
    Timeslot 7 : [29, 30, 31, 32, 33, 34, 35, 36, 75, 97, 98, 100, 101, 129]
    Timeslot 8 : [17, 18, 19, 21, 22, 23, 24, 25, 41, 49, 50, 51, 52, 53, 54, 55, 56, 67, 68, 69]
    Timeslot 9 : [38, 39, 40, 42, 43, 44, 45, 46, 61, 76, 77, 78, 79, 80, 81, 82, 83, 108, 109, 110]
    Timeslot 10 : [5, 6, 7, 58, 59, 60, 62, 63, 64, 65, 66, 88, 111, 112, 113, 114, 115, 116, 117, 118]
    Timeslot 11 : [72, 73, 74, 85, 86, 87, 89, 90, 91, 92, 93, 123]
    The unscheduled exams are [120, 121, 124, 126, 127, 128, 122, 125]
    They have the following sizes [29, 32, 19, 32, 34, 34, 20, 19]
    

As shown, this gives a 12-timeslot solution but leaves 8 unscheduled
exams.

As an alternative, she now tries to minimize the number of clashes by
forming an edge-weighted graph in which each edge :math:`\{v_i,v_j\}`
has a weight equal to :math:`X_{ij}`.

.. code:: ipython3

    #Construct the edge-weighted graph G
    G = nx.Graph()
    for i in range(n):
        if X[i][i] > 0:
            G.add_node(i)
    for i in range(n-1):
        for j in range(i+1, n):
            if X[i][i] > 0 and X[j][j] > 0 and X[i][j] > 0:
                G.add_edge(i, j, weight=X[i][j])
    
    c = gcol.min_cost_k_coloring(G, 12, weight="weight", weights_at="edges", it_limit=10000)
    P = gcol.partition(c)
    print("Here are the exams assigned to each timeslot")
    for i in range(len(P)):
        print("Timeslot", i, ":", P[i])
    print("Here are the clashes in this timetable:")
    for u, v in G.edges():
        if c[u] == c[v]:
            print("Exams", u , "and", v, "assigned to timeslot", c[v], "but have", X[u][v], "common student(s)")


.. parsed-literal::

    Here are the exams assigned to each timeslot
    Timeslot 0 : [2, 3, 133]
    Timeslot 1 : [70, 71, 136]
    Timeslot 2 : [96, 102, 103, 132]
    Timeslot 3 : [47, 131, 134, 135]
    Timeslot 4 : [0, 1, 26, 137, 138]
    Timeslot 5 : [94, 95, 99, 104, 105, 106, 107]
    Timeslot 6 : [4, 8, 9, 10, 11, 12, 13, 14, 15, 20, 23, 28, 40, 48, 63, 120, 121, 124, 127, 128]
    Timeslot 7 : [29, 30, 31, 32, 33, 34, 35, 36, 75, 97, 98, 100, 101, 129]
    Timeslot 8 : [17, 18, 19, 21, 22, 24, 25, 41, 49, 50, 51, 52, 53, 54, 55, 56, 67, 68, 69, 126]
    Timeslot 9 : [38, 39, 42, 43, 44, 45, 46, 61, 76, 77, 78, 79, 80, 81, 82, 83, 108, 109, 110, 122]
    Timeslot 10 : [5, 6, 7, 58, 59, 60, 62, 64, 65, 66, 88, 111, 112, 113, 114, 115, 116, 117, 118, 125]
    Timeslot 11 : [72, 73, 74, 85, 86, 87, 89, 90, 91, 92, 93, 123]
    Here are the clashes in this timetable:
    Exams 26 and 138 assigned to timeslot 4 but have 1 common student(s)
    

As shown, this leads to a 12-timeslot solution in which only one student
is affected by a clash. She submits this solution to her manager who is
so pleased, he gives her a promotion.

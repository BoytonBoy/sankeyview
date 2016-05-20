import networkx as nx

from sankeyview.ordering import (flatten_bands, unflatten_bands, band_index,
                                 new_node_index_flat, new_node_indices,
                                 median_value, neighbour_positions,
                                 fill_unknown)


def test_flatten_bands():
    bands = [['a'], ['b', 'c'], ['d']]
    L, idx = flatten_bands(bands)
    assert L == ['a', 'b', 'c', 'd']
    assert idx == [0, 1, 3]

    bands2 = unflatten_bands(L, idx)
    assert bands2 == bands


def test_band_index():
    # bands:  a | b c | d
    assert band_index([0, 1, 3], 0) == 0
    assert band_index([0, 1, 3], 1) == 1
    assert band_index([0, 1, 3], 2) == 1
    assert band_index([0, 1, 3], 3) == 2
    assert band_index([0, 1, 3], 9) == 2


def test_new_node_index_flat():

    L0 = ['a', 'b']
    L1 = ['x', 'y', 'z']

    # Simple alignment: a--x, n--y, b--z
    G = nx.DiGraph()
    G.add_edges_from([('a', 'x'), ('b', 'z'), ('y', 'n')])
    assert new_node_index_flat(G, L0, L1, 'n') == 1

    # Simple alignment: n--x, a--y, b--z
    G = nx.DiGraph()
    G.add_edges_from([('a', 'y'), ('b', 'z'), ('x', 'n')])
    assert new_node_index_flat(G, L0, L1, 'n') == 0

    # Tie-breaking: {a, n}--x
    L0 = ['a']
    L1 = ['x']
    G = nx.DiGraph()
    G.add_edges_from([('a', 'x'), ('n', 'x')])
    assert new_node_index_flat(G, L0, L1, 'n', side='above') == 0
    assert new_node_index_flat(G, L0, L1, 'n', side='below') == 1
    assert new_node_index_flat(G, L0, L1, 'n') == 1

    # Different number of nodes: {a, b, c}--x, n--y
    L0a = ['a', 'b', 'c']
    L1a = ['x', 'y']
    G = nx.DiGraph()
    G.add_edges_from([('a', 'x'), ('b', 'x'), ('c', 'x'), ('y', 'n')])
    assert new_node_index_flat(G, L0a, L1a, 'n') == 3


def test_new_node_indices():
    # Simple alignment: a--x, n--y || b--z
    bands0 = [ ['a'     ], ['b'] ]
    bands1 = [ ['x', 'y'], ['z'] ]
    G = nx.DiGraph()
    G.add_edges_from([('a', 'x'), ('b', 'z'), ('y', 'n')])
    assert new_node_indices(G, bands0, bands1, 'n') == (0, 1)  # band 0, pos 1

    # Simple alignment: a--x || b--z n--y
    bands0 = [ ['a'], ['b'     ] ]
    bands1 = [ ['x'], ['z', 'y'] ]
    G = nx.DiGraph()
    G.add_edges_from([('a', 'x'), ('b', 'z'), ('y', 'n')])
    assert new_node_indices(G, bands0, bands1, 'n') == (1, 1)  # band 1, pos 1

    # Simple alignment: n--y || a--x b--z
    bands0 = [ [   ], ['a', 'b'] ]
    bands1 = [ ['y'], ['x', 'z'] ]
    G = nx.DiGraph()
    G.add_edges_from([('a', 'x'), ('b', 'z'), ('y', 'n')])
    assert new_node_indices(G, bands0, bands1, 'n') == (0, 0)  # band 0, pos 0

    # Another case
    bands0 = [ ['x'] ]
    bands1 = [ [   ] ]
    G = nx.DiGraph()
    G.add_edge('x', 'n')
    assert new_node_indices(G, bands1, bands0, 'n') == (0, 0)  # band 0, pos 0

    # Another case
    bands0 = [ ['a', 'target', 'b'] ]
    bands1 = [ ['c', 'origin', 'd'] ]
    G = nx.DiGraph()
    G.add_edges_from([ ('a', 'c'), ('b', 'd'), ('origin', 'new') ])
    assert new_node_indices(G, bands0, bands1, 'new', 'above') == (0, 1)
    assert new_node_indices(G, bands0, bands1, 'new', 'below') == (0, 2)


def test_new_node_indices_when_not_connected():
    bands0 = [ ['x'] ]
    bands1 = [ [   ] ]
    G = nx.DiGraph()
    # no edges
    assert new_node_indices(G, bands1, bands0, 'n') == (0, 0)  # default


def test_median_value():
    assert median_value([3, 4, 6]) == 4, 'picks out middle value'

    assert median_value([3, 4]) == 3.5, 'returns average of 2 values'

    assert median_value([]) == -1, 'returns -1 for empty list of positions'

    assert median_value(
        [0, 5, 6, 7, 8, 9
         ]) == 6.75, 'weighted median for even number of positions'


def test_neighbour_positions():
    G, order = _example_two_level()

    assert neighbour_positions(G, order[1], 'n2') == [0, 3, 4], 'n2'
    assert neighbour_positions(G, order[1], 'n0') == [0], 'n0'

    assert neighbour_positions(G, order[0], 's4') == [2, 5], 's4'
    assert neighbour_positions(G, order[0], 's0') == [0, 2, 3], 's0'


def test_fill_unknown():
    assert fill_unknown([0, 1, 2], 'above') == [0, 1, 2]
    assert fill_unknown([0, 1, 2], 'below') == [0, 1, 2]

    assert fill_unknown([0, -1, 2], 'above') == [0, 2, 2]
    assert fill_unknown([0, -1, 2], 'below') == [0, 0, 2]

    assert fill_unknown([], 'above') == []
    assert fill_unknown([], 'below') == []

    assert fill_unknown([-1], 'above') == [1]
    assert fill_unknown([-1], 'below') == [0]
    assert fill_unknown([-1, -1], 'above') == [2, 2]
    assert fill_unknown([-1, -1], 'below') == [0, 0]


def _example_two_level():
    G = nx.DiGraph()

    # Example from Barth2004
    G.add_edges_from([
        ('n0', 's0'),
        ('n1', 's1'),
        ('n1', 's2'),
        ('n2', 's0'),
        ('n2', 's3'),
        ('n2', 's4'),
        ('n3', 's0'),
        ('n3', 's2'),
        ('n4', 's3'),
        ('n5', 's2'),
        ('n5', 's4'),
    ])

    order = [
        ['n0', 'n1', 'n2', 'n3', 'n4', 'n5'],
        ['s0', 's1', 's2', 's3', 's4'],
    ]

    return (G, order)
import pytest

from sankeyview.augment_view_graph import augment, elsewhere_bundles
from sankeyview.node import Node
from sankeyview.bundle import Bundle, Elsewhere
from sankeyview.grouping import Grouping
from sankeyview.view_definition import ViewDefinition
from sankeyview.view_graph import view_graph


# For testing, disable checks on bundles; allows to have waypoints defining
# structure without getting too many extra to/from bundles
class UncheckedViewDefinition(ViewDefinition):
    def __new__(cls, nodes, bundles, order, flow_grouping=None,
                flow_selection=None, time_grouping=None):
        # bypass ViewDefinition __new__
        return super(ViewDefinition, cls).__new__(
            cls, nodes, bundles, order, flow_grouping, flow_selection, time_grouping)


def test_elsewhere_bundles_are_added_when_no_bundles_defined():
    # make it easier to get started
    nodes = {'a': Node(selection=['a1']), }
    bundles = {}
    order = [['a']]
    vd = ViewDefinition(nodes, bundles, order)
    new_nodes, new_bundles = elsewhere_bundles(vd)
    assert len(new_bundles) == 2


def test_elsewhere_bundles_not_added_at_min_max_rank_if_at_least_one_bundle_is_defined():
    nodes = {'a': Node(selection=['a1'])}
    bundles = {0: Bundle('a', Elsewhere)}
    order = [['a']]
    vd = ViewDefinition(nodes, bundles, order)
    new_nodes, new_bundles = elsewhere_bundles(vd)
    assert len(new_nodes) == 0
    assert len(new_bundles) == 0


def test_elsewhere_bundles_not_added_to_waypoints():
    nodes = {'waypoint': Node(), }
    bundles = {}
    order = [[], ['waypoint'], []]
    vd = ViewDefinition(nodes, bundles, order)
    new_nodes, new_bundles = elsewhere_bundles(vd)
    assert new_nodes == {}
    assert new_bundles == {}


def test_elsewhere_bundles():
    nodes = {'a': Node(selection=['a1']), }
    bundles = {}
    order = [[], ['a'], []]  # not at min/max rank
    vd = ViewDefinition(nodes, bundles, order)
    new_nodes, new_bundles = elsewhere_bundles(vd)
    assert set(new_nodes.keys()) == {'__a>', '__>a'}
    assert set(new_bundles.values()) == {
        Bundle('a',
               Elsewhere,
               waypoints=['__a>']),
        Bundle(Elsewhere,
               'a',
               waypoints=['__>a']),
    }

    # assert set(vd2.nodes) == {'a', 'to a', 'from a'}
    # assert vd2.order == [[['to a']], [['a']], [['from a']]]
    # assert vd2.bundles == [
    # ]


def test_elsewhere_bundles_does_not_duplicate():
    nodes = {'a': Node(selection=('a1')), 'in': Node(), 'out': Node(), }
    bundles = {
        0: Bundle(Elsewhere,
                  'a',
                  waypoints=['in']),
        1: Bundle('a',
                  Elsewhere,
                  waypoints=['out']),
    }
    order = [['in'], ['a'], ['out']]  # not at min/max rank
    vd = ViewDefinition(nodes, bundles, order)
    new_nodes, new_bundles = elsewhere_bundles(vd)
    assert new_bundles == {}


def test_augment_waypoint_alignment():
    # j -- a -- x
    #      b
    # k -- c -- y
    #
    # should insert "from b" betwen x and y
    # and "to b" between j and k
    nodes = {
        'a': Node(),
        'b': Node(selection=['b1']),
        'c': Node(),
        'x': Node(),
        'y': Node(),
        'j': Node(),
        'k': Node(),
    }
    bundles = {
        0: Bundle('j', 'a'),
        1: Bundle('k', 'c'),
        2: Bundle('a', 'x'),
        3: Bundle('c', 'y'),
    }

    order = [[['j', 'k']], [['a', 'b', 'c']], [['x', 'y']]]
    vd = UncheckedViewDefinition(nodes, bundles, order)

    G, _ = view_graph(vd)
    new_nodes = {
        'from b': Node(),
        'to b': Node(),
    }
    new_bundles = {
        'b>': Bundle('b',
                     Elsewhere,
                     waypoints=['from b']),
        '>b': Bundle(Elsewhere,
                     'b',
                     waypoints=['to b']),
    }

    G2 = augment(G, new_nodes, new_bundles)

    assert set(G2.nodes()).difference(G.nodes()) == {'from b', 'to b'}
    assert G2.order == [
        [['j', 'to b', 'k']],
        [['a', 'b', 'c']],
        [['x', 'from b', 'y']]
    ]


# def test_augment_adds_elsewhere_bundles_reversed():
#     nodes = {'a': Node(selection=['a1'], direction='L'), }
#     bundles = []
#     order = [[], ['a'], []]  # not at min/max rank
#     vd = ViewDefinition(nodes, bundles, order)
#     vd2 = augment(vd)

#     assert set(vd2.nodes) == {'a', 'to a', 'from a'}
#     assert vd2.order == [[['from a']], [['a']], [['to a']]]
#     assert vd2.bundles == [
#         Bundle('a',
#                Elsewhere,
#                waypoints=['from a']),
#         Bundle(Elsewhere,
#                'a',
#                waypoints=['to a']),
#     ]


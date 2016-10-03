import pytest

from sankeyview.augment_view_graph import augment, elsewhere_bundles
from sankeyview.partition import Partition
from sankeyview.sankey_definition import SankeyDefinition, Ordering, ProcessGroup, Waypoint, Bundle, Elsewhere
from sankeyview.view_graph import view_graph


def test_elsewhere_bundles_are_added_when_no_bundles_defined():
    # make it easier to get started
    nodes = {'a': ProcessGroup(selection=['a1']), }
    bundles = {}
    order = [['a']]
    vd = SankeyDefinition(nodes, bundles, order)
    new_process_groups, new_bundles = elsewhere_bundles(vd)
    assert len(new_bundles) == 2


def test_elsewhere_bundles_not_added_at_min_max_rank_if_at_least_one_bundle_is_defined():
    nodes = {'a': ProcessGroup(selection=['a1'])}
    bundles = {0: Bundle('a', Elsewhere)}
    order = [['a']]
    vd = SankeyDefinition(nodes, bundles, order)
    new_process_groups, new_bundles = elsewhere_bundles(vd)
    assert len(new_process_groups) == 0
    assert len(new_bundles) == 0


def test_elsewhere_bundles_not_added_to_waypoints():
    nodes = {'waypoint': Waypoint(), }
    bundles = {}
    order = [[], ['waypoint'], []]
    vd = SankeyDefinition(nodes, bundles, order)
    new_process_groups, new_bundles = elsewhere_bundles(vd)
    assert new_process_groups == {}
    assert new_bundles == {}


def test_elsewhere_bundles():
    nodes = {'a': ProcessGroup(selection=['a1']), }
    bundles = {}
    order = [[], ['a'], []]  # not at min/max rank
    vd = SankeyDefinition(nodes, bundles, order)
    new_process_groups, new_bundles = elsewhere_bundles(vd)
    assert set(new_process_groups.keys()) == {'__a>', '__>a'}
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
    nodes = {
        'a': ProcessGroup(selection=('a1')),
        'in': Waypoint(),
        'out': Waypoint()
    }
    bundles = {
        0: Bundle(Elsewhere,
                  'a',
                  waypoints=['in']),
        1: Bundle('a',
                  Elsewhere,
                  waypoints=['out']),
    }
    order = [['in'], ['a'], ['out']]  # not at min/max rank
    vd = SankeyDefinition(nodes, bundles, order)
    new_process_groups, new_bundles = elsewhere_bundles(vd)
    assert new_bundles == {}


@pytest.mark.usefixtures('disable_attr_validators')
def test_augment_waypoint_alignment():
    # j -- a -- x
    #      b
    # k -- c -- y
    #
    # should insert "from b" betwen x and y
    # and "to b" between j and k
    nodes = {
        'a': ProcessGroup(),
        'b': ProcessGroup(selection=['b1']),
        'c': ProcessGroup(),
        'x': ProcessGroup(),
        'y': ProcessGroup(),
        'j': ProcessGroup(),
        'k': ProcessGroup(),
    }
    bundles = {
        0: Bundle('j', 'a'),
        1: Bundle('k', 'c'),
        2: Bundle('a', 'x'),
        3: Bundle('c', 'y'),
    }

    order = [[['j', 'k']], [['a', 'b', 'c']], [['x', 'y']]]
    vd = SankeyDefinition(nodes, bundles, order)

    G, _ = view_graph(vd)
    new_process_groups = {
        'from b': ProcessGroup(),
        'to b': ProcessGroup(),
    }
    new_bundles = {
        'b>': Bundle('b',
                     Elsewhere,
                     waypoints=['from b']),
        '>b': Bundle(Elsewhere,
                     'b',
                     waypoints=['to b']),
    }

    G2 = augment(G, new_process_groups, new_bundles)

    assert set(G2.nodes()).difference(G.nodes()) == {'from b', 'to b'}
    assert G2.ordering == Ordering([
        [['j', 'to b', 'k']],
        [['a', 'b', 'c']],
        [['x', 'from b', 'y']]
    ])


# def test_augment_adds_elsewhere_bundles_reversed():
#     nodes = {'a': ProcessGroup(selection=['a1'], direction='L'), }
#     bundles = []
#     order = [[], ['a'], []]  # not at min/max rank
#     vd = SankeyDefinition(nodes, waypoints, bundles, order)
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


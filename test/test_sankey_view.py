import pytest

import pandas as pd

from sankeyview.view_definition import ViewDefinition, Ordering, ProcessGroup, Waypoint, Bundle
from sankeyview.sankey_view import sankey_view
from sankeyview.partition import Partition
from sankeyview.dataset import Dataset


def test_sankey_view_results():
    process_groups = {
        'a': ProcessGroup(selection=['a1', 'a2']),
        'b': ProcessGroup(selection=['b1']),
        'c': ProcessGroup(selection=['c1', 'c2'], partition=Partition.Simple('node', ['c1', 'c2'])),
    }
    waypoints = {
        'via': Waypoint(partition=Partition.Simple('material', ['m', 'n'])),
    }
    bundles = [
        Bundle('a', 'c', waypoints=['via']),
        Bundle('b', 'c', waypoints=['via']),
    ]
    ordering = [
        [['a', 'b']], [['via']], [['c']]
    ]
    vd = ViewDefinition(process_groups, waypoints, bundles, ordering)

    # Dataset
    flows = pd.DataFrame.from_records([
        ('a1', 'c1', 'm', 3),
        ('a2', 'c1', 'n', 1),
        ('b1', 'c1', 'm', 1),
        ('b1', 'c2', 'm', 2),
        ('b1', 'c2', 'n', 1),
    ], columns=('source', 'target', 'material', 'value'))
    processes = pd.DataFrame({
        'id': list(flows.source.unique()) + list(flows.target.unique())}).set_index('id')
    dataset = Dataset(processes, flows)

    GR, groups = sankey_view(vd, dataset)

    assert set(GR.nodes()) == {'a^*', 'b^*', 'via^m', 'via^n', 'c^c1', 'c^c2'}
    assert sorted(GR.edges(keys=True, data=True)) == [
        ('a^*',   'via^m', ('*', '*'), { 'value': 3, 'bundles': [0] }),
        ('a^*',   'via^n', ('*', '*'), { 'value': 1, 'bundles': [0] }),
        ('b^*',   'via^m', ('*', '*'), { 'value': 3, 'bundles': [1] }),
        ('b^*',   'via^n', ('*', '*'), { 'value': 1, 'bundles': [1] }),
        ('via^m', 'c^c1',  ('*', '*'), { 'value': 4, 'bundles': [0, 1] }),
        ('via^m', 'c^c2',  ('*', '*'), { 'value': 2, 'bundles': [0, 1] }),
        ('via^n', 'c^c1',  ('*', '*'), { 'value': 1, 'bundles': [0, 1] }),
        ('via^n', 'c^c2',  ('*', '*'), { 'value': 1, 'bundles': [0, 1] }),
    ]

    assert GR.ordering == Ordering([
        [ ['a^*', 'b^*'] ],
        [ ['via^m', 'via^n'] ],
        [ ['c^c1', 'c^c2'] ],
    ])
    assert groups == [
        {'id': 'a',   'title': '', 'type': 'process', 'bundle': None, 'def_pos': None, 'nodes': ['a^*']},
        {'id': 'b',   'title': '', 'type': 'process', 'bundle': None, 'def_pos': None, 'nodes': ['b^*']},
        {'id': 'via', 'title': '', 'type': 'group',   'bundle': None, 'def_pos': None, 'nodes': ['via^m', 'via^n']},
        {'id': 'c',   'title': '', 'type': 'process', 'bundle': None, 'def_pos': None, 'nodes': ['c^c1', 'c^c2']},
    ]

    # Can also set flow_partition for all bundles at once
    vd2 = ViewDefinition(process_groups, waypoints, bundles, ordering,
                         flow_partition=Partition.Simple('material', ['m', 'n']))
    GR, groups = sankey_view(vd2, dataset)
    assert sorted(GR.edges(keys=True, data=True)) == [
        ('a^*',   'via^m', ('m', '*'), { 'value': 3, 'bundles': [0] }),
        ('a^*',   'via^n', ('n', '*'), { 'value': 1, 'bundles': [0] }),
        ('b^*',   'via^m', ('m', '*'), { 'value': 3, 'bundles': [1] }),
        ('b^*',   'via^n', ('n', '*'), { 'value': 1, 'bundles': [1] }),
        ('via^m', 'c^c1',  ('m', '*'), { 'value': 4, 'bundles': [0, 1] }),
        ('via^m', 'c^c2',  ('m', '*'), { 'value': 2, 'bundles': [0, 1] }),
        ('via^n', 'c^c1',  ('n', '*'), { 'value': 1, 'bundles': [0, 1] }),
        ('via^n', 'c^c2',  ('n', '*'), { 'value': 1, 'bundles': [0, 1] }),
    ]


def test_sankey_view_results_time_partition():
    process_groups = {
        'a': ProcessGroup(selection=['a1']),
        'b': ProcessGroup(selection=['b1']),
    }
    waypoints = {}
    bundles = [Bundle('a', 'b')]
    ordering = [[['a']], [['b']]]
    time_partition = Partition.Simple('time', [1, 2])
    vd = ViewDefinition(process_groups, waypoints, bundles, ordering, time_partition=time_partition)

    # Dataset
    flows = pd.DataFrame.from_records([
        ('a1', 'b1', 'm', 1, 3),
        ('a1', 'b1', 'm', 2, 2),
    ], columns=('source', 'target', 'material', 'time', 'value'))
    processes = pd.DataFrame({'id': ['a1', 'b1']}).set_index('id')
    dataset = Dataset(processes, flows)

    GR, groups = sankey_view(vd, dataset)
    assert set(GR.nodes()) == {'a^*', 'b^*'}
    assert sorted(GR.edges(keys=True, data=True)) == [
        ('a^*', 'b^*', ('*', '1'), { 'value': 3, 'bundles': [0] }),
        ('a^*', 'b^*', ('*', '2'), { 'value': 2, 'bundles': [0] }),
    ]
    assert GR.ordering == Ordering([ [['a^*']], [['b^*']] ])


# @pytest.mark.xfail
# def test_sankey_view_adds_bundles_to_from_elsewhere():
#     nodes = {
#         # this is a real node -- should add 'to elsewhere' bundle
#         # should not add 'from elsewhere' bundle as it would be the only one
#         'a': ProcessGroup(0, 0, query=('a1')),
#         'b': ProcessGroup(1, 0, query=('b1')),

#         # this is a waypoint -- should not have from/to via nodes
#         'via': ProcessGroup(0, 0),
#     }
#     bundles = [Bundle('a', 'b')]
#     v = SankeyView(nodes, bundles)

#     from_a = ProcessGroup(1, 0)
#     to_b = ProcessGroup(0, 0)
#     assert set(v.nodes) == {nodes['a'], nodes['b'], nodes['via'], from_a, to_b}
#     assert sorted(v.bundles) == [
#         Bundle('a', 'b'),
#         Bundle('a', Elsewhere, waypoints=['from a']),
#         Bundle(Elsewhere, 'b', waypoints=['to b']),
#     ]


# @pytest.mark.xfail
# def test_sankey_view_allows_only_one_bundle_to_or_from_elsewhere():
#     nodes = {
#         'a': ProcessGroup(0, 0, query=('a1', 'a2')),
#     }
#     bundles = [
#         Bundle(Elsewhere, 'a'),
#         Bundle(Elsewhere, 'a'),
#     ]
#     with pytest.raises(ValueError):
#         SankeyView(nodes, bundles)

#     bundles = [
#         Bundle('a', Elsewhere),
#         Bundle('a', Elsewhere),
#     ]
#     with pytest.raises(ValueError):
#         SankeyView(nodes, bundles)

#     bundles = [
#         Bundle('a', Elsewhere),
#     ]
#     SankeyView(nodes, bundles)


# def edges_ignoring_elsewhere(v, data=False):
#     if data:
#         return [(a, b, data) for a, b, data in v.high_level.edges(data=True)
#                 if not (a.startswith('from') or b.startswith('from') or
#                         a.startswith('to') or b.startswith('to'))]
#     else:
#         return [(a, b) for a, b in v.high_level.edges(data=False)
#                 if not (a.startswith('from') or b.startswith('from') or
#                         a.startswith('to') or b.startswith('to'))]


# def nodes_ignoring_elsewhere(v):
#     return [u for u in v.high_level.nodes(data=False)
#             if not (u.startswith('from') or u.startswith('to'))]

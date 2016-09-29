import networkx as nx

from .view_definition import ProcessGroup, Waypoint, Bundle, Elsewhere
from .ordering import new_node_indices, Ordering


def elsewhere_bundles(view_definition):
    # Build set of existing bundles to/from elsewhere
    has_to_elsewhere = set()
    has_from_elsewhere = set()
    for bundle in view_definition.bundles.values():
        assert not (bundle.source is Elsewhere and bundle.target is Elsewhere)
        if bundle.target is Elsewhere:
            # XXX they might have different flow_selections?
            # if bundle.source in has_to_elsewhere:
            #     raise ValueError('duplicate bundles to elsewhere from {}'.format(bundle.source))
            has_to_elsewhere.add(bundle.source)
        if bundle.source is Elsewhere:
            # XXX they might have different flow_selections?
            # if bundle.target in has_from_elsewhere:
            #     raise ValueError('duplicate bundles from elsewhere to {}'.format(bundle.target))
            has_from_elsewhere.add(bundle.target)

    # For each process_group, add new bundles to/from elsewhere if not already
    # existing. Each one should have a waypoint of rank +/- 1.
    R = len(view_definition.ordering.layers)
    new_process_groups = {}
    new_bundles = {}

    # Add elsewhere bundles to all process_groups if there are no bundles to start with
    no_bundles = (len(view_definition.bundles) == 0)

    for u, process_group in view_definition.process_groups.items():
        if not process_group.selection:
            continue  # no waypoints
        d_rank = +1 if process_group.direction == 'R' else -1
        r, _, _ = view_definition.ordering.indices(u)

        if no_bundles or (0 <= r + d_rank < R and u not in has_to_elsewhere):
            dummy_id = '__{}>'.format(u)
            assert dummy_id not in view_definition.process_groups
            new_process_groups[dummy_id] = ProcessGroup(direction=process_group.direction)
            new_bundles[dummy_id] = Bundle(u, Elsewhere, waypoints=[dummy_id])

        if no_bundles or (0 <= r - d_rank < R and u not in has_from_elsewhere):
            dummy_id = '__>{}'.format(u)
            assert dummy_id not in view_definition.process_groups
            new_process_groups[dummy_id] = ProcessGroup(direction=process_group.direction)
            new_bundles[dummy_id] = Bundle(Elsewhere, u, waypoints=[dummy_id])

    return new_process_groups, new_bundles



def augment(G, new_process_groups, new_bundles):
    """Add waypoints for new_bundles to layered graph G"""

    # copy G and order
    G = G.copy()

    R = len(G.ordering.layers)
    for k, bundle in new_bundles.items():
        assert len(bundle.waypoints) == 1
        w = bundle.waypoints[0]

        if bundle.to_elsewhere:
            u = G.node[bundle.source]['node']
            r, _, _ = G.ordering.indices(bundle.source)
            d_rank = +1 if u.direction == 'R' else -1
            G.add_node(w, node=new_process_groups[w])

            r, G.ordering = check_order_edges(G.ordering, r, d_rank)

            this_rank = G.ordering.layers[r + d_rank]
            prev_rank = G.ordering.layers[r]
            G.add_edge(bundle.source, w, bundles=[k])
            i, j = new_node_indices(G, this_rank, prev_rank, w,
                                    side='below') # if d == 'L' else 'above')

            G.ordering = G.ordering.insert(r + d_rank, i, j, w)

        elif bundle.from_elsewhere:
            u = G.node[bundle.target]['node']
            r, _, _ = G.ordering.indices(bundle.target)
            d_rank = +1 if u.direction == 'R' else -1
            G.add_node(w, node=new_process_groups[w])

            r, G.ordering = check_order_edges(G.ordering, r, -d_rank)

            this_rank = G.ordering.layers[r - d_rank]
            prev_rank = G.ordering.layers[r]
            G.add_edge(w, bundle.target, bundles=[k])
            i, j = new_node_indices(G, this_rank, prev_rank, w,
                                    side='below') # if d == 'L' else 'above')

            G.ordering = G.ordering.insert(r - d_rank, i, j, w)

        else:
            assert False, "Should not call augment() with non-elsewhere bundle"

    return G


def check_order_edges(ordering, r, dr):
    layers = ordering.layers
    nb = len(layers[0]) if layers else 1
    if r + dr >= len(layers):
        layers = layers + tuple(() for i in range(nb))
    elif r + dr < 0:
        layers = tuple(() for i in range(nb)) + layers
        r += 1
    return r, Ordering(layers)

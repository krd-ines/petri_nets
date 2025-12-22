from tree.algo import KMGraph
from tree.markings import OMEGA

# ---------------------------------------------------------------------
# boundedness (NO PRINTS AS REQUESTED)
def is_bounded(graph: KMGraph):
    max_tokens = 0
    for node in graph.nodes:
        for v in node.marking.values():
            if v == OMEGA:
                return False
            if v > max_tokens:
                max_tokens = v
    return max_tokens


# ---------------------------------------------------------------------
# quasi-liveness (transition-level)
def quasi_live_transitions(graph: KMGraph, transitions: set[str]) -> dict[str, bool]:
    print("[quasi_live_transitions] Checking per-transition quasi-liveness")

    fired = {t: False for t in transitions}

    for edge in graph.edges:
        print(f"  Transition fired: {edge.transition}")
        fired[edge.transition] = True

    print("[quasi_live_transitions] Result:", fired)
    return fired


# ---------------------------------------------------------------------
# quasi-liveness (net)
def is_quasi_live(graph: KMGraph, all_transitions: set[str]) -> bool:
    print("[is_quasi_live] Checking net quasi-liveness")

    fired = {arc.transition for arc in graph.edges}

    print("  Fired transitions:", fired)
    print("  All transitions:", all_transitions)

    result = fired == all_transitions
    print("  Quasi-live =", result)

    return result


# ---------------------------------------------------------------------
# resettable
def is_resettable(graph: KMGraph) -> bool:
    print("[is_resettable] Checking resettable property")

    root_id = 0

    reverse = {n.id: [] for n in graph.nodes}
    for e in graph.edges:
        reverse[e.dst].append(e.src)

    print("  Reverse adjacency:", reverse)

    visited = set()
    stack = [root_id]

    while stack:
        n = stack.pop()
        if n not in visited:
            print(f"  Visiting node {n}")
            visited.add(n)
            stack.extend(reverse[n])

    result = len(visited) == len(graph.nodes)
    print("  Reachable nodes:", visited)
    print("  Resettable =", result)

    return result


# ---------------------------------------------------------------------
# detect dead-ends
def has_deadend(graph: KMGraph) -> bool:
    print("[has_deadend] Checking for dead-end nodes")

    for n in graph.nodes:
        print(f"  Node {n.id} tag = {n.tag}")
        if n.tag == "dead-end":
            print("  Dead-end detected")
            return True

    print("  No dead-end detected")
    return False


# ---------------------------------------------------------------------
# adjacency
def build_children(graph: KMGraph) -> dict[int, list[int]]:
    print("[build_children] Building adjacency list")

    children = {n.id: [] for n in graph.nodes}
    for e in graph.edges:
        children[e.src].append(e.dst)

    print("  Children map:", children)
    return children


# ---------------------------------------------------------------------
# subtree transitions
def compute_subtree_transitions(graph: KMGraph):
    print("[compute_subtree_transitions] Computing subtree transitions")

    node_transitions = {}

    for n in graph.nodes:
        print(f"  Starting from node {n.id}")
        visited = set()
        node_transitions[n.id] = collect_subtree_transitions_from(
            graph, n.id, visited
        )
        print(f"    Reachable transitions: {node_transitions[n.id]}")

    return node_transitions


def collect_subtree_transitions_from(
    graph: KMGraph,
    start_node: int,
    visited: set[int]
) -> set[str]:
    print(f"    [collect] Visiting node {start_node}")

    if start_node in visited:
        print(f"    [collect] Node {start_node} already visited, stopping")
        return set()

    visited.add(start_node)
    fired = set()

    for e in graph.edges:
        if e.src == start_node:
            print(f"    [collect] Found transition {e.transition} to node {e.dst}")
            fired.add(e.transition)
            fired |= collect_subtree_transitions_from(
                graph, e.dst, visited
            )

    return fired


# ---------------------------------------------------------------------
# liveness (transition)
def is_transition_live(transition: str, subtree_transitions: dict[int, set[str]]) -> bool:
    print(f"[is_transition_live] Checking liveness of transition {transition}")

    for node_id, fired in subtree_transitions.items():
        print(f"  Node {node_id} can fire {fired}")
        if transition not in fired:
            print("  Transition NOT live")
            return False

    print("  Transition is live")
    return True


# ---------------------------------------------------------------------
# liveness (net)
def is_net_live(graph: KMGraph, all_transitions: set[str]) -> bool:
    print("[is_net_live] Checking net liveness")

    # 1. dead-end
    if has_deadend(graph):
        print("  Net is NOT live (dead-end)")
        return False

    # 2. shortcut
    if is_quasi_live(graph, all_transitions) and is_resettable(graph):
        print("  Net is LIVE (quasi-live + resettable)")
        return True

    # 3. full check
    subtree = compute_subtree_transitions(graph)
    transitions = {arc.transition for arc in graph.edges}

    for t in transitions:
        print(f"  Checking transition {t}")
        for node_id, fired in subtree.items():
            print(f"    Node {node_id}: {fired}")
            if t not in fired:
                print("  Net is NOT live")
                return False

    print("  Net is LIVE (full check)")
    return True

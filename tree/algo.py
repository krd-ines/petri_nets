from dataclasses import dataclass, field
from typing import List
from snakes.nets import PetriNet

from tree.markings import Marking, markings_identical, markings_equal_greater, accelerate, OMEGA
from tree.matrices import extract_pre_post
from tree.transitions import enabled, fire

# ---------------------------------------------------------------------
# class representing the tree nodes = markings
@dataclass
class Node:
    id: int
    marking: Marking
    tag: str = "new"  

# ---------------------------------------------------------------------
# class for transition arcs between nodes
@dataclass
class Arc:
    src: int # source node id
    dst: int # destination node id
    transition: str # transition name

# ---------------------------------------------------------------------
# class for the tree = graph (nodes + arcs)
@dataclass
class KMGraph:
    nodes: List[Node] = field(default_factory=list)
    edges: List[Arc] = field(default_factory=list)

# ---------------------------------------------------------------------
# build the coverability tree
def build_coverability_tree(net: PetriNet, M0: Marking) -> KMGraph:
    # pre + post matrices
    PRE, POST = extract_pre_post(net)
    # new graph
    graph = KMGraph()

    # root node = initial marking = new tag
    graph.nodes.append(Node(0, M0))
    # queue to track new markings
    queue = [0]  

    # as long as there are new nodes
    while queue:
        # select marking
        nid = queue.pop(0) 
        node = graph.nodes[nid]

        if node.tag != "new":
            continue
        node.tag = "done" 

        # ancestors = markings from root to current marking
        ancestors = [
            graph.nodes[e.src].marking
            for e in graph.edges
            if e.dst == nid
        ]

        # check transactions (franchissable?)
        for t in PRE:
            if not enabled(node.marking, PRE[t]): 
                continue

            # franchir(fire) for new marking
            m_prime = fire(node.marking, PRE[t], POST[t])

            # if cover -> accelerate -> omega
            for m_old in ancestors:
                if markings_equal_greater(m_prime, m_old) and not markings_identical(m_prime, m_old):
                    m_prime = accelerate(m_prime, m_old)

            # check if marking already exists
            existing = next(
                (n for n in graph.nodes if markings_identical(n.marking, m_prime)),
                None
            )

            if existing:
                # if existing, add arc
                graph.edges.append(Arc(nid, existing.id, t))
            else:
                # else add node + arc
                new_id = len(graph.nodes)
                graph.nodes.append(Node(new_id, m_prime))
                graph.edges.append(Arc(nid, new_id, t))
                # "new" marking
                queue.append(new_id)  

    return graph






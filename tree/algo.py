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

    # root is the first node
    graph.nodes.append(Node(0, M0, tag="new"))
    queue = [0]  

    while queue:
        nid = queue.pop(0) 
        node = graph.nodes[nid]

        # old = check if marking was already defined
        is_old = any(
            n.id < node.id and markings_identical(n.marking, node.marking) 
            for n in graph.nodes
        )
        
        if is_old:
            node.tag = "old"
            print(f"  [TAG] Noeud {nid} marqué comme 'old' (déjà vu).")
            continue
        
        # else done
        node.tag = "done" 
        
        # check ancestors for acceleration
        ancestors_nodes = []
        current_search = nid
        while current_search != 0:
            for e in graph.edges:
                if e.dst == current_search:
                    ancestors_nodes.append(graph.nodes[e.src])
                    current_search = e.src
                    break
        ancestors_nodes.append(graph.nodes[0])

        any_enabled = False 

        for t in PRE:
            if not enabled(node.marking, PRE[t]): 
                continue

            any_enabled = True 
            m_prime = fire(node.marking, PRE[t], POST[t])

            # acceleration
            for anc in ancestors_nodes:
                if markings_equal_greater(m_prime, anc.marking) and not markings_identical(m_prime, anc.marking):
                    print(f"  [OMEGA] Accélération détectée entre Noeud {nid} et Ancêtre {anc.id}")
                    m_prime = accelerate(m_prime, anc.marking)

            # node existence check
            existing = next(
                (n for n in graph.nodes if markings_identical(n.marking, m_prime)),
                None
            )

            if existing:
                graph.edges.append(Arc(nid, existing.id, t))
            else:
                new_id = len(graph.nodes)
                # new node
                graph.nodes.append(Node(new_id, m_prime, tag="new"))
                graph.edges.append(Arc(nid, new_id, t))
                queue.append(new_id)  

        # dead-end check
        if not any_enabled:
            node.tag = "dead-end"
            print(f"  [TAG] Noeud {nid} marqué comme 'dead-end' (blocage).")

    return graph






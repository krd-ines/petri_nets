from dataclasses import dataclass, field
from typing import List
from snakes.nets import PetriNet
import copy
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
# build the coverability tree with history tracking
def build_tree_with_history(net: PetriNet, M0: Marking):
    # pre + post matrices
    PRE, POST = extract_pre_post(net)
    graph = KMGraph()
    history = [] 

    # new initial node
    root_node = Node(0, M0, tag="new")
    graph.nodes.append(root_node)
    queue = [0]
    
    # history message
    history.append((copy.deepcopy(graph), f"Initial node created with marking {format_marking(M0)}"))

    while queue:
        nid = queue.pop(0) 
        node = graph.nodes[nid]

        # check if marking already exists
        is_old = any(
            n.id < node.id and markings_identical(n.marking, node.marking) 
            for n in graph.nodes
        )
        
        if is_old:
            node.tag = "old"
            # history message
            history.append((copy.deepcopy(graph), f"Node {nid} {format_marking(node.marking)} is an existing marking. No expansion."))
            continue
        
        # find all ancestor (parent) nodes
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

        # explore all transitions from current marking
        for t in PRE:
            if not enabled(node.marking, PRE[t]): 
                continue

            any_enabled = True 
            m_prime = fire(node.marking, PRE[t], POST[t])
            
            # acceleration check
            accel_msg = ""
            for anc in ancestors_nodes:
                if markings_equal_greater(m_prime, anc.marking) and not markings_identical(m_prime, anc.marking):
                    m_prime = accelerate(m_prime, anc.marking)
                    accel_msg = f" (Accelerated with Node {anc.id})"

            # ckeck if new marking already exists
            existing = next((n for n in graph.nodes if markings_identical(n.marking, m_prime)), None)

            if existing:
                # if exists, just add edge
                graph.edges.append(Arc(nid, existing.id, t))
                # history message
                history.append((copy.deepcopy(graph), f"Transition {t} leads to existing marking {format_marking(m_prime)}{accel_msg}"))
            else:
                # else, create new node and edge
                new_id = len(graph.nodes)
                graph.nodes.append(Node(new_id, m_prime, tag="new"))
                graph.edges.append(Arc(nid, new_id, t))
                queue.append(new_id)
                # history message
                history.append((copy.deepcopy(graph), f"Fired {t}: Created Node {new_id} with marking {format_marking(m_prime)}{accel_msg}"))

        # update node tag based
        if any_enabled:
            node.tag = "done"
            history.append((copy.deepcopy(graph), f"Finished exploring all transitions for Node {nid}."))
        else:
            node.tag = "dead-end"
            history.append((copy.deepcopy(graph), f"Node {nid} {format_marking(node.marking)} is a dead-end."))
    return graph, history

# ---------------------------------------------------------------------
# marking -> string
def format_marking(marking) -> str:
        return "(" + ",".join(
        "\u03c9" if v == OMEGA else str(v)
        for v in marking.values()
    ) + ")"
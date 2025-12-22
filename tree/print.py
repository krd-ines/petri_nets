
from tree.algo import KMGraph
from tree.markings import OMEGA


# ---------------------------------------------------------------------
# marking -> string
def format_marking(marking) -> str:
        return "(" + ",".join(
        OMEGA if v == OMEGA else str(v)
        for v in marking.values()
    ) + ")"

# print nodes + maekings
def print_nodes(graph: KMGraph):
    print("\nNodes:")
    for n in graph.nodes:
        print(f"  N{n.id}: {format_marking(n.marking)} tag='{n.tag}'")

# print transition arcs (src --transition--> dst)
def print_edges(graph: KMGraph):
    print("\nArcs:")
    for e in graph.edges:
        print(f"  N{e.src} --{e.transition}--> N{e.dst}")

# print graph
def print_graph(graph: KMGraph):
    print_nodes(graph)
    print_edges(graph)

from tree.algo import KMGraph, format_marking
from tree.markings import OMEGA

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

from tree.algo import KMGraph
from tree.print import format_marking
from graphviz import Source


# ---------------------------------------------------------------------
# export graph to DOT format (Graphviz)
def to_dot(graph: KMGraph) -> str:
    lines = ["digraph KM {", "  rankdir=LR;"] 

    # nodes with labels
    for n in graph.nodes:
        label = format_marking(n.marking)
        lines.append(f'  N{n.id} [label="{label}"];')

    # arcs with transition labels
    for e in graph.edges:
        lines.append(f'  N{e.src} -> N{e.dst} [label="{e.transition}"];')

    lines.append("}")
    return "\n".join(lines)

# ---------------------------------------------------------------------
# DOT -> image file
def save_graph_image(graph: KMGraph, filename: str = "km_graph", fmt: str = "png") -> None:

    dot_str = to_dot(graph)
    src = Source(dot_str)
    src.format = fmt
    src.render(filename, cleanup=True)  
    print(f"Graph saved as {filename}.{fmt}")

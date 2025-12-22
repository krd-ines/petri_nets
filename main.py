from snakes.nets import Value, PetriNet, Place, Transition
from tree.algo import build_coverability_tree
from tree.markings import OMEGA
from tree.print import print_graph
from tree.export import save_graph_image
from tree.properties import is_bounded, is_quasi_live, is_resettable, is_net_live
from net.create import create_net




# -------------------------------
# build the petri net
net = PetriNet("example_net")

# places
for pname in ["p1", "p2", "p3", "p4", "p5"]:
    tokens = 0
    if pname in ["p2", "p4"]:
        tokens = 1  # initial marking
    net.add_place(Place(pname, tokens=tokens))

# transitions
for tname in ["t1", "t2", "t3", "t4"]:
    net.add_transition(Transition(tname))

# arcs (pre/post)
# t1: pre {p1, p3, p4}, post {p2}
net.add_input("p1", "t1", Value(1))
net.add_input( "p3", "t1", Value(1))
net.add_output( "p2", "t1", Value(1))
net.add_input( "p4", "t1", Value(1))

# t2: pre {p2}, post {p1}
net.add_input("p2", "t2", Value(1))
net.add_output( "p1", "t2",Value(1))

# t3: pre {p5}, post {p3, p4}
net.add_input("p5", "t3", Value(1))
net.add_output( "p3", "t3", Value(1))
net.add_output( "p4", "t3", Value(1))

# t4: pre {p4}, post {p5}
net.add_input("p4", "t4", Value(1))
net.add_output( "p5", "t4", Value(1))

transitions = net.transition()

# -------------------------------
# initial marking
initial_marking = {p.name: sum(p.tokens) for p in net.place()}
print("Initial marking:", initial_marking)

# -------------------------------
# coverability tree
tree = build_coverability_tree(net, initial_marking)

# -------------------------------
# print tree
print_graph(tree)

# -------------------------------
# export to dot
save_graph_image(tree, "graph")

print("\nProperties of the net:")
print("- Bounded:", False if not is_bounded(tree) else f"True (bound {is_bounded(tree)})")
print("- Quasi-live: ", is_quasi_live(tree, transitions))
print("- Resettable:", is_resettable(tree))
print("- Live:", is_net_live(tree, transitions))










# ----------------------------------------
# anotehr example
print("\n--- Another example net ---\n")
net_simple = create_net("simple_net")

# Places with initial tokens
for pname in ["p1", "p2", "p3"]:
    tokens = 0
    if pname == "p1":
        tokens = 2  # initial marking
    net_simple.add_place(Place(pname, tokens=tokens))

# Transitions
for tname in ["t1", "t2", "t3"]:
    net_simple.add_transition(Transition(tname))

# Arcs

# t1: p1 -> p2
net_simple.add_input("p1", "t1", Value(1))
net_simple.add_output("p2", "t1", Value(1))

# t2: p2 -> p3
net_simple.add_input("p2", "t2", Value(1))
net_simple.add_output("p3", "t2", Value(1))

# t3: p3 -> p1
net_simple.add_input("p3", "t3", Value(1))
net_simple.add_output("p1", "t3", Value(1))

transitions = net_simple.transition()

# -------------------------------
# initial marking
initial_marking = {p.name: sum(p.tokens) for p in net_simple.place()}
print("Initial marking:", initial_marking)

# -------------------------------
# coverability tree
tree = build_coverability_tree(net_simple, initial_marking)

# -------------------------------
# print tree
print_graph(tree)

# -------------------------------
# export to dot
save_graph_image(tree, "graph2")

print("\nProperties of the net:")
print("- Bounded:", False if not is_bounded(tree) else f"True (bound {is_bounded(tree)})")
print("- Quasi-live: ", is_quasi_live(tree, transitions))
print("- Resettable:", is_resettable(tree))
print("- Live:", is_net_live(tree, transitions))
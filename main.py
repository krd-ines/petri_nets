from snakes.nets import Value, PetriNet, Place, Transition
from tree.algo import build_coverability_tree
from tree.markings import OMEGA
from tree.print import print_graph
from tree.export import save_graph_image




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

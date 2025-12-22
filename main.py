from snakes.nets import PetriNet, Place, Transition, Value, MultiArc  # Added MultiArc
from tree.algo import build_coverability_tree
from tree.print import print_graph
from tree.export import save_graph_image
from tree.properties import is_bounded, is_quasi_live, is_resettable, is_net_live
from net.create import create_net

# # -------------------------------
# # Example frontend data
# circles = [{'label': 'p0', 'tokens': 2}, {'label': 'p1', 'tokens': 0}]
# squares = [{'label': 't0'}]
# arrows = [
#     {'start_label': 'p0', 'end_label': 't0', 'weight': 1},
#     {'start_label': 't0', 'end_label': 'p1', 'weight': 2}
# ]

# # -------------------------------
# # Build the Petri net
# net = PetriNet("frontend_net")

# # 1. Add places
# for c in circles:
#     count = c.get('tokens', 0)
#     # Create 'count' number of black tokens
#     tokens_list = [Value(1) for _ in range(count)]
#     net.add_place(Place(c['label'], tokens=tokens_list))

# # 2. Add transitions
# for s in squares:
#     net.add_transition(Transition(s['label']))

# # 3. Add arcs (FIXED with MultiArc)
# for a in arrows:
#     start, end = a['start_label'], a['end_label']
#     weight = a.get('weight', 1)

#     # --- FIX STARTS HERE ---
#     if weight == 1:
#         # Single token
#         arc_val = Value(1)
#     else:
#         # Multiple tokens: Use MultiArc to bundle them
#         # Creates a list like [Value(1), Value(1), ...]
#         arc_val = MultiArc([Value(1) for _ in range(weight)])
#     # --- FIX ENDS HERE ---

#     if start.startswith("p") and end.startswith("t"):
#         net.add_input(start, end, arc_val)
#     elif start.startswith("t") and end.startswith("p"):
#         net.add_output(end, start, arc_val)

# transitions = net.transition()

# # -------------------------------
# # 4. Initial marking
# initial_marking = {p.name: len(p.tokens) for p in net.place()}
# print("Initial marking:", initial_marking)

# # -------------------------------
# # coverability tree
# tree = build_coverability_tree(net, initial_marking)

# # -------------------------------
# # print tree
# print_graph(tree)

# # -------------------------------
# # export to dot
# save_graph_image(tree, "graph")

# print("\nProperties of the net:")
# print("- Bounded:", False if not is_bounded(tree) else f"True (bound {is_bounded(tree)})")
# print("- Quasi-live: ", is_quasi_live(tree, transitions))
# print("- Resettable:", is_resettable(tree))
# print("- Live:", is_net_live(tree, transitions))










# ----------------------------------------
# another example
print("\n--- Another example net ---\n")
net_simple = create_net("simple_net")

# Places with initial tokens
for pname in ["p1", "p2", "p3"]:
    tokens = 0
    if pname == "p1":
        tokens = 1  # initial marking
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
bound = is_bounded(tree)
print("- Bounded:", False if not bound else f"True (bound {bound})")
print("- Quasi-live: ", is_quasi_live(tree, transitions))
print("- Resettable:", is_resettable(tree))
print("- Live:", is_net_live(tree, transitions))
# # Coverability tree
# try:
#     tree = build_coverability_tree(net, initial_marking)
#     print_graph(tree)
#     save_graph_image(tree, "graph")
#     print("Graph exported successfully as 'graph.png'")
# except Exception as e:
#     print(f"Error building tree: {e}")

# net = PetriNet("example_net_5_places")

# # Places
# for pname in ["p1", "p2", "p3", "p4", "p5"]:
#     tokens = 0
#     if pname in ["p2", "p4"]:
#         tokens = 1   # initial marking
#     net.add_place(Place(pname, tokens=tokens))

# # Transitions
# for tname in ["t1", "t2", "t3", "t4"]:
#     net.add_transition(Transition(tname))

# # -----------------------------
# # Arcs
# # -----------------------------

# # t1: p1 + p3 + p4 -> p2
# net.add_input("p1", "t1", Value(1))
# net.add_input("p3", "t1", Value(1))
# net.add_input("p4", "t1", Value(1))
# net.add_output("p2", "t1", Value(1))

# # t2: p2 -> p1
# net.add_input("p2", "t2", Value(1))
# net.add_output("p1", "t2", Value(1))

# # t3: p5 -> p3 + p4
# net.add_input("p5", "t3", Value(1))
# net.add_output("p3", "t3", Value(1))
# net.add_output("p4", "t3", Value(1))

# # t4: p4 -> p5
# net.add_input("p4", "t4", Value(1))
# net.add_output("p5", "t4", Value(1))

# transitions = net.transition()

# # -------------------------------
# # initial marking
# initial_marking = {p.name: sum(p.tokens) for p in net.place()}
# print("Initial marking:", initial_marking)

# # -------------------------------
# # coverability tree
# tree = build_coverability_tree(net, initial_marking)

# # -------------------------------
# # print tree
# print_graph(tree)

# # -------------------------------
# # export to dot
# save_graph_image(tree, "graph")

# print("\nProperties of the net:")
# print("- Bounded:", False if not is_bounded(tree) else f"True (bound {is_bounded(tree)})")
# print("- Quasi-live: ", is_quasi_live(tree, transitions))
# print("- Resettable:", is_resettable(tree))
# print("- Live:", is_net_live(tree, transitions))

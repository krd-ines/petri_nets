from snakes.nets import PetriNet, Place, Transition, Value, MultiArc  # Added MultiArc
from tree.algo import build_coverability_tree
from tree.print import print_graph
from tree.export import save_graph_image

# -------------------------------
# Example frontend data
circles = [{'label': 'p0', 'tokens': 2}, {'label': 'p1', 'tokens': 0}]
squares = [{'label': 't0'}]
arrows = [
    {'start_label': 'p0', 'end_label': 't0', 'weight': 1},
    {'start_label': 't0', 'end_label': 'p1', 'weight': 2}
]

# -------------------------------
# Build the Petri net
net = PetriNet("frontend_net")

# 1. Add places
for c in circles:
    count = c.get('tokens', 0)
    # Create 'count' number of black tokens
    tokens_list = [Value(1) for _ in range(count)]
    net.add_place(Place(c['label'], tokens=tokens_list))

# 2. Add transitions
for s in squares:
    net.add_transition(Transition(s['label']))

# 3. Add arcs (FIXED with MultiArc)
for a in arrows:
    start, end = a['start_label'], a['end_label']
    weight = a.get('weight', 1)

    # --- FIX STARTS HERE ---
    if weight == 1:
        # Single token
        arc_val = Value(1)
    else:
        # Multiple tokens: Use MultiArc to bundle them
        # Creates a list like [Value(1), Value(1), ...]
        arc_val = MultiArc([Value(1) for _ in range(weight)])
    # --- FIX ENDS HERE ---

    if start.startswith("p") and end.startswith("t"):
        net.add_input(start, end, arc_val)
    elif start.startswith("t") and end.startswith("p"):
        net.add_output(end, start, arc_val)

# -------------------------------
# 4. Initial marking
initial_marking = {p.name: len(p.tokens) for p in net.place()}
print("Initial marking:", initial_marking)

# -------------------------------
# Coverability tree
try:
    tree = build_coverability_tree(net, initial_marking)
    print_graph(tree)
    save_graph_image(tree, "graph")
    print("Graph exported successfully as 'graph.png'")
except Exception as e:
    print(f"Error building tree: {e}")
# GraphViz Test

from graphviz import Digraph
from snakes.nets import PetriNet  # type: ignore

def draw_petri_net(net: PetriNet, filename: str = "petri_net") -> None:
    dot = Digraph(name=net.name, format="png")

    # ---- Places ----
    for place in net.place():
        # Ordinary Petri nets: tokens stored under key 1
        token_count = place.tokens.get(1, 0)
        label = f"{place.name}\n({token_count})"
        dot.node(place.name, label=label, shape="circle")

    # ---- Transitions ----
    for transition in net.transition():
        dot.node(transition.name, label=transition.name, shape="box")

    # ---- Arcs: place -> transition (inputs) ----
    for transition in net.transition():
        for place, arc in transition.input():
            weight = arc.value  # Arc is a Value object
            dot.edge(place.name, transition.name, label=str(weight))

    # ---- Arcs: transition -> place (outputs) ----
    for transition in net.transition():
        for place, arc in transition.output():
            weight = arc.value
            dot.edge(transition.name, place.name, label=str(weight))

    # Render and save
    dot.render(filename, cleanup=True)

from snakes.nets import PetriNet, Place, Transition, Value

# ---------------------------------------------------------------------
# create a Petri net
def create_net(name: str) -> PetriNet:
    return PetriNet(name)

# ---------------------------------------------------------------------
# add place
def add_place(net: PetriNet, name: str, tokens: int = 0) -> None:
    net.add_place(Place(name, tokens=tokens))

# ---------------------------------------------------------------------
# add transition
def add_transition(net: PetriNet, name: str) -> None:
    net.add_transition(Transition(name))

# ---------------------------------------------------------------------
# add pre
def add_input_arc(net: PetriNet, place: str, transition: str, weight: int = 1) -> None:
    net.add_input(place, transition, Value(weight))

# ---------------------------------------------------------------------
# add post
def add_output_arc(net: PetriNet, transition: str, place: str, weight: int = 1) -> None:
    net.add_output(place, transition,  Value(weight))

# ---------------------------------------------------------------------
# get marking as dicttionary place -> token
def get_marking_as_dict(net: PetriNet) -> dict[str, int]:
    marking: dict[str, int] = {}

    for place in net.place():
        marking[place.name] = place.tokens.get(1, 0)

    return marking



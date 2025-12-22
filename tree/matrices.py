from snakes.nets import PetriNet ,MultiArc  # type: ignore

# ---------------------------------------------------------------------
# extract pre and post from snakes petri net
def extract_pre_post(net: PetriNet):

    PRE = {t.name: {} for t in net.transition()}
    POST = {t.name: {} for t in net.transition()}

    # 1. Fill PRE matrix (Inputs)
    for p in net.place():
        for t_name, label in p.post.items():
            # If the arc carries multiple tokens (MultiArc)
            if isinstance(label, MultiArc):
                PRE[t_name][p.name] = len(label)
            # If the arc carries one token (Value)
            else:
                PRE[t_name][p.name] = label.value

    # 2. Fill POST matrix (Outputs)
    for p in net.place():
        for t_name, label in p.pre.items():
            if isinstance(label, MultiArc):
                POST[t_name][p.name] = len(label)
            else:
                POST[t_name][p.name] = label.value

    return PRE, POST

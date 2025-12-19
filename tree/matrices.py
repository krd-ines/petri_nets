from snakes.nets import PetriNet  # type: ignore

# ---------------------------------------------------------------------
# extract pre and post from snakes petri net
def extract_pre_post(net: PetriNet):

    PRE = {t.name: {} for t in net.transition()}
    POST = {t.name: {} for t in net.transition()}

    # pre
    for p in net.place():
        for t_name, label in p.post.items():
            PRE[t_name][p.name] = label.value

    # post
    for p in net.place():
        for t_name, label in p.pre.items():
            POST[t_name][p.name] = label.value

    return PRE, POST

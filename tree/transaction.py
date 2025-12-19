from typing import Dict
from tree.markings import Marking, OMEGA, is_omega

# ---------------------------------------------------------------------
# check if a transition is enabled at a given marking (franchissable)
def enabled(marking: Marking, pre: Dict[str, int]) -> bool:
    # check pre matrix
    for p, w in pre.items():
        if is_omega(marking[p]):  
            # omega = enough tokens
            continue
        if marking[p] < w:
            return False
    return True


# ---------------------------------------------------------------------
# fire = franchir transition -> new marking
def fire(marking: Marking, pre, post) -> Marking:
    new: Marking = {}
    # copy current marking
    for p in marking:
        if is_omega(marking[p]):
            new[p] = OMEGA
        else:
            new[p] = marking[p]

    # remove tokens from pre places
    for p, w in pre.items():
        if not is_omega(new[p]):
            new[p] -= w

    # add tokens to post places
    for p, w in post.items():
        if not is_omega(new[p]): 
            new[p] += w

    return new

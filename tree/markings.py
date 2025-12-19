from typing import Dict, Union

# infinity = omega
OMEGA = "w"

# token = number or omega
Token = Union[int, str] 

# marking = place -> token
Marking = Dict[str, Token]

# ---------------------------------------------------------------------
# check if a token value is omega or not
def is_omega(token: Token) -> bool:
    return token == OMEGA


# ---------------------------------------------------------------------
# check if two markings are identical
def markings_identical(m1: Marking, m2: Marking) -> bool:
    return all(m1[p] == m2[p] for p in m1)


# ---------------------------------------------------------------------
# check if m1 >= m2
def markings_equal_greater(m1: Marking, m2: Marking) -> bool:
    for p in m1:
        # omega >= anything
        if is_omega(m1[p]):
            continue 
        # number < omega 
        if is_omega(m2[p]):
            return False  
        if m1[p] < m2[p]:
            return False 
    return True


# ---------------------------------------------------------------------
# accelerate = token -> omega
def accelerate(m_prime: Marking, m_old: Marking) -> Marking:
    result: Marking = {}
    for p in m_prime:
        if is_omega(m_old[p]) or is_omega(m_prime[p]) or m_prime[p] > m_old[p]:
            # if old = omega, keep omega
            # if new = omega, keep omega
            # if new  > old, replace with omega
            result[p] = OMEGA
        else:
            # else, keep value
            result[p] = m_prime[p]
    return result

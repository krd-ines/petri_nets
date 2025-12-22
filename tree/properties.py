from tree.algo import KMGraph
from tree.markings import OMEGA

# ---------------------------------------------------------------------
# retrieve all possible transitions
def _get_transition_names(transitions: set) -> set[str]:
    # list -> string
    return {t.name if hasattr(t, "name") else t for t in transitions}

# ---------------------------------------------------------------------
# retrieve all fired transitions in the graph
def _get_fired_in_graph(graph: KMGraph) -> set[str]:
    return {edge.transition for edge in graph.edges}

# ---------------------------------------------------------------------
# dead-end detection
def has_deadend(graph: KMGraph) -> bool:
    print("[has_deadend] Checking for dead-end nodes")
    for n in graph.nodes:
        print(f"  Node {n.id} tag = {n.tag}")
        if n.tag == "dead-end":
            print("  Dead-end detected")
            return True
    print("  No dead-end detected")
    return False

# ---------------------------------------------------------------------
# boundedness
def is_bounded(graph: KMGraph):
    print("\n[STEP 1: Analyse de la Bornetude]")
    max_tokens = 0
    for node in graph.nodes:
        print(f"  > Analyse du Noeud {node.id} (marquage: {node.marking})")
        for p, v in node.marking.items():
            if v == OMEGA:
                print(f"    ! DETECTION : Place '{p}' contient OMEGA. Le réseau est NON-BORNÉ.")
                return False
            if v > max_tokens:
                max_tokens = v
    print(f"  -> RESULTAT : Réseau borné. Valeur max trouvée : {max_tokens}")
    return max_tokens

# ---------------------------------------------------------------------
# quasi-liveness per transition
def quasi_live_per_transition(graph: KMGraph, transitions: set) -> dict[str, bool]:
    print("\n[STEP 2: QUASI-VIVACITÉ INDIVIDUELLE]")
    all_names = _get_transition_names(transitions)
    fired_names = _get_fired_in_graph(graph)
    
    print(f"  > Transitions définies dans le réseau : {all_names}")
    print(f"  > Transitions observées dans le graphe : {fired_names}")
    
    result = {t: (t in fired_names) for t in all_names}
    for t, status in result.items():
        print(f"    - {t} : {'[OK] Apparaît dans le graphe' if status else '[KO] JAMAIS activée'}")
    return result

# net quasi-liveness
def is_quasi_live(graph: KMGraph, all_transitions: set) -> bool:
    print("\n[STEP 3: QUASI-VIVACITÉ GLOBALE]")
    all_names = _get_transition_names(all_transitions)
    fired_names = _get_fired_in_graph(graph)
    
    missing = all_names - fired_names
    if missing:
        print(f"  -> RESULTAT : Faux. Les transitions suivantes bloquent la quasi-vivacité : {missing}")
        return False
    print("  -> RESULTAT : Vrai. Chaque transition possède au moins un arc dans le graphe.")
    return True

# ----------------------------------------------------------------------
# resettable
def is_resettable(graph: KMGraph) -> bool:
    print("\n[STEP 4: ANALYSE DE LA RÉINITIALISATION (RETOUR À M0)]")
    # reverse graph nodes -> root
    reversed = {n.id: [] for n in graph.nodes}
    for e in graph.edges:
        reversed[e.dst].append(e.src)
    print(f"  > Graphe inverse construit : {reversed}")

    # passed this node or not
    visited = set()
    stack = [0]
    print("  > Début du parcours inverse depuis le Noeud 0...")
    
    while stack:
        curr = stack.pop()
        if curr not in visited:
            print(f"    - Noeud {curr} peut revenir à M0")
            visited.add(curr)
            stack.extend(reversed[curr])
    
    result = len(visited) == len(graph.nodes)
    print(f"  > Noeuds connectés à M0 : {len(visited)}/{len(graph.nodes)}")
    print(f"  -> RESULTAT : Réinitialisable = {result}")
    return result

# ----------------------------------------------------------------------
# find reachable transitions from each node
def reachable_transitions(graph: KMGraph) -> dict[int, set[str]]:
    print("\n[STEP 5: CALCUL DE L'ACCESSIBILITÉ DES TRANSITIONS]")
    adj = {n.id: [] for n in graph.nodes}
    for e in graph.edges:
        adj[e.src].append((e.dst, e.transition))

    node_reachability = {}
    for start_node in graph.nodes:
        print(f"  > Exploration depuis Noeud {start_node.id}...")
        reachable_t = set()
        stack = [start_node.id]
        visited_nodes = set()
        
        while stack:
            u = stack.pop()
            if u not in visited_nodes:
                visited_nodes.add(u)
                for v, trans_name in adj[u]:
                    reachable_t.add(trans_name)
                    stack.append(v)
        node_reachability[start_node.id] = reachable_t
        print(f"    - Transitions atteignables : {reachable_t if reachable_t else 'AUCUNE'}")
        
    return node_reachability

# liveness per transition
def liveness_per_transition(graph: KMGraph, all_transitions: set) -> dict[str, bool]:
    print("\n[STEP 6: VIVACITÉ PAR TRANSITION (CRITÈRE DE SURVIE)]")
    all_names = _get_transition_names(all_transitions)
    reach_map = reachable_transitions(graph)
    
    results = {}
    for t in all_names:
        print(f"  > Vérification de la survie de {t} :")
        is_live = True
        for node_id, reachable in reach_map.items():
            if t not in reachable:
                print(f"    ! Échec : {t} est perdue si on atteint le Noeud {node_id}")
                is_live = False
                break
        results[t] = is_live
        if is_live:
            print(f"    -> {t} est VIVE (toujours atteignable)")
            
    return results

# ----------------------------------------------------------------------
# net liveness
def is_net_live(graph: KMGraph, all_transitions: set) -> bool:
    print("\n[STEP 7: AUDIT FINAL DE VIVACITÉ DU RÉSEAU]")
    # dead-end
    if has_deadend(graph):
        print("  Net is NOT live (dead-end)")
        return False

    # quasi + resettable
    if is_quasi_live(graph, all_transitions) and is_resettable(graph):
        print("  Net is LIVE (quasi-live + resettable)")
        return True

    # per transition liveness
    t_results = liveness_per_transition(graph, all_transitions)
    net_live = all(t_results.values())
    
    print(f"\n  -> SYNTHÈSE : Le réseau est-il vivant ? {'OUI' if net_live else 'NON'}")
    return net_live
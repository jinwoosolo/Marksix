from __future__ import annotations
from itertools import combinations
import math
import numpy as np


def wheel_space_size(core_n: int=12, secondary_n: int=32, last_choices: int=1) -> int:
    return math.comb(core_n,2) * math.comb(secondary_n,3) * last_choices


def candidate_tickets(core, secondary, last_pool=None, max_candidates: int=150000, seed: int=42):
    core = sorted(set(map(int,core)))
    secondary = sorted(set(map(int,secondary)))
    base_count = math.comb(len(core),2) * math.comb(len(secondary),3)
    rng = np.random.default_rng(seed)
    out = set()
    # Full enumeration is ~327k 5-number skeletons for 12/32, manageable but avoid huge UI payloads.
    skeletons = ((a,b) for a in combinations(core,2) for b in combinations(secondary,3))
    if base_count <= max_candidates:
        chosen = list(skeletons)
    else:
        # Reservoir-like randomized sampling via index-free repeated draws.
        chosen = []
        seen = set()
        while len(chosen) < max_candidates:
            a = tuple(sorted(rng.choice(core,2,replace=False).tolist()))
            b = tuple(sorted(rng.choice(secondary,3,replace=False).tolist()))
            key=(a,b)
            if key not in seen:
                seen.add(key); chosen.append(key)
    universe = sorted(set(core)|set(secondary)) if last_pool is None else sorted(set(map(int,last_pool)))
    for a,b in chosen:
        used=set(a)|set(b)
        allowed=[n for n in universe if n not in used]
        if not allowed:
            continue
        # Use one sixth number per skeleton at candidate-generation stage; optimizer diversifies globally.
        sixth = int(rng.choice(allowed))
        out.add(tuple(sorted((*a,*b,sixth))))
    return sorted(out)


def optimize_tickets(candidates, score_map, ticket_count: int=20, overlap_penalty: float=0.22):
    if ticket_count <= 0:
        return []
    remaining = list(candidates)
    selected=[]
    def base_score(t):
        return sum(float(score_map.get(n,0.0)) for n in t)
    while remaining and len(selected)<ticket_count:
        best=None; bestv=-1e99
        for t in remaining[:50000]:
            overlap = 0.0 if not selected else max(len(set(t)&set(s))/6 for s in selected)
            v=base_score(t)-overlap_penalty*overlap
            if v>bestv:
                bestv=v; best=t
        if best is None: break
        selected.append(best)
        remaining.remove(best)
    return selected


def prize_class(ticket, main_numbers, extra):
    t=set(ticket); main=set(main_numbers)
    m=len(t & main); e=int(extra in t)
    if m==6: return '1st'
    if m==5 and e: return '2nd'
    if m==5: return '3rd'
    if m==4 and e: return '4th'
    if m==4: return '5th'
    if m==3 and e: return '6th'
    if m==3: return '7th'
    return None

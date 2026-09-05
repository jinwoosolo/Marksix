from __future__ import annotations
from itertools import combinations
import math
import numpy as np


def wheel_space_size(core_n: int = 12, secondary_n: int = 32, last_choices: int = 1) -> int:
    return math.comb(core_n, 2) * math.comb(secondary_n, 3) * last_choices


def unique_full_wheel_size(core, secondary, last_pool=None) -> int:
    """Count unique 6-number tickets representable by 2 Core + 3 Secondary + Any 1.

    A representable ticket has at least 2 Core and at least 3 Secondary.  The sixth
    number may be another Core, another Secondary, or Lowest if included in last_pool.
    """
    core = set(map(int, core)); sec = set(map(int, secondary))
    universe = core | sec if last_pool is None else set(map(int, last_pool))
    low = universe - core - sec
    total = 0
    # possible compositions of a six-number ticket under the structural rule
    for c in range(2, 7):
        for s in range(3, 7 - c):
            l = 6 - c - s
            if l < 0:
                continue
            if c <= len(core) and s <= len(sec) and l <= len(low):
                total += math.comb(len(core), c) * math.comb(len(sec), s) * math.comb(len(low), l)
    return total


def _ticket_score(ticket, score_map):
    vals = [float(score_map.get(n, 0.0)) for n in ticket]
    # Sum drives ranking; a small floor reward avoids concentrating every ticket
    # around one very high-ranked cluster.
    return float(sum(vals) + 0.10 * min(vals))


def candidate_tickets(core, secondary, last_pool=None, score_map=None,
                      max_candidates: int = 60000, seed: int = 42):
    """Generate unique candidate tickets satisfying Core>=2 and Secondary>=3.

    Candidate generation samples structural compositions rather than assigning one
    random sixth number to every 5-number skeleton.  This makes 2C+4S, 3C+3S and
    2C+3S+1L all available when the sixth-number pool allows them.
    """
    core = sorted(set(map(int, core)))
    secondary = sorted(set(map(int, secondary)))
    universe = set(core) | set(secondary) if last_pool is None else set(map(int, last_pool))
    lowest = sorted(universe - set(core) - set(secondary))
    rng = np.random.default_rng(seed)
    out = set()

    compositions = []
    for c, s, l in [(2, 4, 0), (3, 3, 0), (2, 3, 1)]:
        if c <= len(core) and s <= len(secondary) and l <= len(lowest):
            count = math.comb(len(core), c) * math.comb(len(secondary), s) * (math.comb(len(lowest), l) if l else 1)
            if count:
                compositions.append((c, s, l, count))
    if not compositions:
        return []

    total_space = sum(x[3] for x in compositions)
    # Exhaustively enumerate only when small; otherwise stratified sampling.
    if total_space <= max_candidates:
        for c, s, l, _ in compositions:
            low_combos = list(combinations(lowest, l)) if l else [()]
            for a in combinations(core, c):
                for b in combinations(secondary, s):
                    for d in low_combos:
                        out.add(tuple(sorted((*a, *b, *d))))
    else:
        weights = np.array([x[3] for x in compositions], dtype=float)
        weights /= weights.sum()
        attempts = 0
        max_attempts = max_candidates * 25
        while len(out) < max_candidates and attempts < max_attempts:
            attempts += 1
            idx = int(rng.choice(len(compositions), p=weights))
            c, s, l, _ = compositions[idx]
            a = rng.choice(core, c, replace=False).tolist()
            b = rng.choice(secondary, s, replace=False).tolist()
            d = rng.choice(lowest, l, replace=False).tolist() if l else []
            out.add(tuple(sorted(map(int, a + b + d))))

    candidates = list(out)
    if score_map:
        candidates.sort(key=lambda t: _ticket_score(t, score_map), reverse=True)
    else:
        candidates.sort()
    return candidates


def optimize_tickets(candidates, score_map, ticket_count: int = 20,
                     overlap_penalty: float = 0.55, number_balance_penalty: float = 0.10,
                     shortlist: int = 12000):
    """Greedy budget-constrained optimizer balancing score, overlap and number usage."""
    if ticket_count <= 0:
        return []
    ranked = sorted(candidates, key=lambda t: _ticket_score(t, score_map), reverse=True)
    remaining = ranked[:max(shortlist, ticket_count * 30)]
    selected = []
    usage = {n: 0 for n in range(1, 50)}
    max_base = max((_ticket_score(t, score_map) for t in remaining), default=1.0)
    min_base = min((_ticket_score(t, score_map) for t in remaining), default=0.0)
    span = max(max_base - min_base, 1e-9)

    while remaining and len(selected) < ticket_count:
        best = None; best_v = -1e99
        # evaluate a bounded frontier to keep Streamlit responsive
        for t in remaining[:min(len(remaining), shortlist)]:
            base = (_ticket_score(t, score_map) - min_base) / span
            overlap = 0.0 if not selected else max(len(set(t) & set(s)) / 6 for s in selected)
            balance = sum(usage[n] for n in t) / max(1, 6 * max(1, len(selected)))
            v = base - overlap_penalty * overlap - number_balance_penalty * balance
            if v > best_v:
                best_v = v; best = t
        if best is None:
            break
        selected.append(best)
        for n in best:
            usage[n] += 1
        remaining.remove(best)
    return selected


def ticket_diagnostics(tickets, core, secondary, lowest):
    core, secondary, lowest = set(core), set(secondary), set(lowest)
    rows = []
    for i, t in enumerate(tickets, 1):
        st = set(t)
        rows.append({
            'Ticket': i,
            'core_n': len(st & core),
            'secondary_n': len(st & secondary),
            'lowest_n': len(st & lowest),
            'numbers': ' '.join(f'{n:02d}' for n in t),
        })
    return rows


def prize_class(ticket, main_numbers, extra):
    t = set(ticket); main = set(main_numbers)
    m = len(t & main); e = int(extra in t)
    if m == 6: return '1st'
    if m == 5 and e: return '2nd'
    if m == 5: return '3rd'
    if m == 4 and e: return '4th'
    if m == 4: return '5th'
    if m == 3 and e: return '6th'
    if m == 3: return '7th'
    return None

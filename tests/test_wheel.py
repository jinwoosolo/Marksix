from src.wheel import candidate_tickets,optimize_tickets,prize_class

def test_candidates_are_six_unique():
    c=candidate_tickets(range(1,13),range(13,45),max_candidates=200)
    assert c
    assert all(len(t)==6 and len(set(t))==6 for t in c)

def test_optimizer_count():
    c=candidate_tickets(range(1,13),range(13,45),max_candidates=200)
    s={n:float(n)/49 for n in range(1,50)}
    out=optimize_tickets(c,s,10)
    assert len(out)==10

def test_prize():
    assert prize_class((1,2,3,4,5,6),(1,2,3,4,5,6),7)=='1st'
    assert prize_class((1,2,3,4,5,7),(1,2,3,4,5,6),7)=='2nd'

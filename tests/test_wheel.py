from src.wheel import candidate_tickets, optimize_tickets, prize_class, unique_full_wheel_size


def pools():
    core=list(range(1,13)); secondary=list(range(13,45)); lowest=list(range(45,50))
    return core,secondary,lowest


def test_candidate_structure_top44():
    core,secondary,lowest=pools()
    c=candidate_tickets(core,secondary,last_pool=core+secondary,max_candidates=500,seed=1)
    assert c
    for t in c:
        st=set(t)
        assert len(st)==6
        assert len(st&set(core))>=2
        assert len(st&set(secondary))>=3
        assert not (st&set(lowest))


def test_candidate_structure_all49():
    core,secondary,lowest=pools()
    c=candidate_tickets(core,secondary,last_pool=list(range(1,50)),max_candidates=1000,seed=2)
    assert c
    for t in c:
        st=set(t)
        assert len(st&set(core))>=2
        assert len(st&set(secondary))>=3


def test_optimizer_count_unique():
    core,secondary,_=pools()
    score={n:float(n) for n in range(1,50)}
    c=candidate_tickets(core,secondary,last_pool=list(range(1,50)),score_map=score,max_candidates=2000)
    t=optimize_tickets(c,score,ticket_count=20)
    assert len(t)==20
    assert len(set(t))==20


def test_unique_full_wheel_size_positive():
    core,secondary,_=pools()
    assert unique_full_wheel_size(core,secondary,list(range(1,50))) > 0


def test_prize_class():
    ticket=(1,2,3,4,5,6)
    assert prize_class(ticket,[1,2,3,4,5,6],7)=='1st'
    assert prize_class(ticket,[1,2,3,4,5,7],6)=='2nd'

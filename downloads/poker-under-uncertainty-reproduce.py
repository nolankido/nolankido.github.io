#!/usr/bin/env python3
"""Reproduce fictional calculations, not player results or optimal strategies.

Python 3.10+; exact calculations use only the standard library.
Optional: --monte-carlo requires NumPy 2.3.5 to reproduce the recorded sample.
Use away from play and follow the actual platform's assistance rules.
"""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, permutations
from math import comb, exp, sqrt
from statistics import NormalDist
import argparse, json, sys

DECK=tuple(r+s for r in '23456789TJQKA' for s in 'shdc')
HERO=('As','Ks')
BOARD=('Js','7d','2s','4c')
RANGE=(('JJ',F(1)),('77',F(1)),('22',F(1)),('AJs',F(3,4)),
       ('KJs',F(3,4)),('QJs',F(3,4)),('T9s',F(1,2)),('98s',F(1,2)),
       ('QTs',F(1,2)),('AQs',F(1,4)))

def five(cards):
    ranks=sorted(('23456789TJQKA'.index(c[0])+2 for c in cards),reverse=True)
    counts=Counter(ranks);groups=sorted(counts.values(),reverse=True)
    order=sorted(counts,key=lambda r:(counts[r],r),reverse=True)
    unique=sorted(counts);flush=len({c[1] for c in cards})==1
    straight=5 if unique==[2,3,4,5,14] else unique[-1] if len(unique)==5 and unique[-1]-unique[0]==4 else 0
    if flush and straight:return (8,straight)
    if groups==[4,1]:return (7,*order)
    if groups==[3,2]:return (6,*order)
    if flush:return (5,*ranks)
    if straight:return (4,straight)
    if groups==[3,1,1]:return (3,*order)
    if groups==[2,2,1]:return (2,*order)
    if groups==[2,1,1,1]:return (1,*order)
    return (0,*ranks)

def best(cards):return max(five(c) for c in combinations(cards,5))

def legal_hands(label, known):
    return [h for h in combinations(DECK,2) if not set(h)&set(known)
            and sorted(c[0] for c in h)==sorted(label[:2])
            and (len(label)==2 or (h[0][1]==h[1][1] if label[2]=='s' else h[0][1]!=h[1][1]))]

def exact_range():
    known=set(HERO+BOARD);rows=[];total=F(0);mass=F(0)
    for label,weight in RANGE:
        hands=legal_hands(label,known);share=F(0)
        for hand in hands:
            for river in DECK:
                if river in known or river in hand:continue
                h=best(HERO+BOARD+(river,));o=best(hand+BOARD+(river,))
                share+=F(1) if h>o else F(1,2) if h==o else F(0)
        equity=share/(44*len(hands));effective=len(hands)*weight
        rows.append({'holding':label,'combos':len(hands),'weight':str(weight),
                     'effective_mass':str(effective),'river_equity':str(equity)})
        total+=share/44*weight;mass+=effective
    return rows,mass,total/mass

def river_masses():
    board=BOARD+('Kd',);known=set(HERO+board);losing=F(0);worse=F(0);unpaired=F(0)
    for label,weight in RANGE:
        for hand in legal_hands(label,known):
            hero=best(HERO+board);opponent=best(hand+board)
            if hero<opponent:losing+=weight
            elif hero==opponent:raise AssertionError('No tie was assumed')
            elif label in ['AJs','QJs']:worse+=weight
            else:unpaired+=weight
    return losing,worse,unpaired

def icm(stacks,prizes):
    equity=[F(0) for _ in stacks]
    for order in permutations(range(len(stacks))):
        probability=F(1);remaining=sum(stacks)
        for place,player in enumerate(order):
            probability*=F(stacks[player],remaining);remaining-=stacks[player]
        for place,player in enumerate(order):equity[player]+=probability*prizes[place]
    return equity

def beta_quantile(probability,a,b):
    # For integer parameters, the beta CDF is a binomial upper-tail sum.
    n=a+b-1;lo=0.;hi=1.
    for _ in range(100):
        x=(lo+hi)/2
        cdf=sum(comb(n,j)*x**j*(1-x)**(n-j) for j in range(a,n+1))
        if cdf<probability:lo=x
        else:hi=x
    return (lo+hi)/2

def exact_results():
    rows,mass,equity=exact_range();losing,worse,weak=river_masses()
    required=F(65,F(305,2)+65);value_mass=losing*F(9,10);pair_mass=worse*F(3,20)
    boundary=(required*value_mass/(1-required)-pair_mass)/weak
    def river(x):
        share=(pair_mass+weak*x)/(value_mass+pair_mass+weak*x)
        return {'x':str(x),'equity':str(share),'call_ev_bb':str(share*F(435,2)-65)}
    before=icm([50,30,20],[50,30,20]);win=icm([20,60,20],[50,30,20])[1]
    z=NormalDist().inv_cdf(.975);power=NormalDist().inv_cdf(.8)
    prior=[F(3,10),F(9,20),F(1,4)];likelihood=[F(4,5),F(3,5),F(1,5)]
    posterior=[p*l for p,l in zip(prior,likelihood)];normalizer=sum(posterior)
    n=12;observed=F(3,12);den=1+z*z/n
    center=(float(observed)+z*z/(2*n))/den
    half=z*sqrt(float(observed*(1-observed))/n+z*z/(4*n*n))/den
    return {'scope':'Fictional models, not a strategy or real-player performance estimate',
      'cards':{'hero':HERO,'turn_board':BOARD,'legal_combinations':rows,'mass':str(mass),'equity':str(equity)},
      'river':{'board':BOARD+('Kd',),'strong_mass':str(losing),'worse_pair_mass':str(worse),
               'weaker_unpaired_mass':str(weak),'threshold':str(required),'boundary':str(boundary),
               'examples':[river(F(7,20)),river(F(1,2))]},
      'draw':{'combinations':comb(52,2),'classes':13+78+78,'flops':comb(50,3),
              'at_least_one_pair_rank_on_flop':str(1-F(comb(48,3),comb(50,3))),
              'exact_flush_by_river':str(1-F(comb(38,2),comb(47,2))),
              'outs':[{'outs':k,'turn':str(F(k,47)),'river':str(1-F(47-k,47)*F(46-k,46))} for k in [2,4,6,8,9,10,12,15]]},
      'bayes':{'prior':[str(p) for p in prior],'likelihood':[str(p) for p in likelihood],
               'posterior':[str(p/normalizer) for p in posterior]},
      'frequency':{'wilson_n':12,'successes':3,'beta_prior':[6,24],'posterior':[9,33],
                   'mean':str(F(9,42)),'wilson_95':[center-half,center+half],
                   'equal_tail_95':[beta_quantile(.025,9,33),beta_quantile(.975,9,33)]},
      'win_rate':{'sigma_per_block_bb':90,'z95_used':1.96,
                  'precision_hands_for_mean_3_using_1_96':(1.96*90/3)**2*100,
                  'approx_80_power_hands':((z+power)*90/3)**2*100,
                  'half_widths':[{'hands':n,'se_bb_per_100':90/sqrt(n/100),'half_width':1.96*90/sqrt(n/100)} for n in [1000,10000,100000,1000000]]},
      'icm':{'before':[str(x) for x in before],'hero_win_equity':str(win),
             'break_even_q':str((before[1]-20)/(win-20))},
      'ledger':{'pots':[22.5,37.5,87.5,217.5],
                 'stacks_before_turn':[131.5,131.5],'stacks_after_turn_call':[106.5,106.5],
                 'stacks_after_river_call':[41.5,41.5]},
      'brownian':{'time_unit':'one 100-hand block','sigma_bb':90,
                  'probabilities':[{'mu_bb':mu,'bankroll_bb':bank,'ruin_probability':exp(-2*mu*bank/90**2)} for mu in [3,5] for bank in [2000,3000,5000]]}}

def monte_carlo():
    import numpy as np
    rng=np.random.default_rng(20261014);n=1_000_000
    estimate=float(np.mean(rng.hypergeometric(9,38,2,size=n)>0));se=sqrt(estimate*(1-estimate)/n)
    return {'numpy':np.__version__,'python':sys.version.split()[0],'seed':20261014,'n':n,
            'estimate':estimate,'se':se,'normal_95':[estimate-1.96*se,estimate+1.96*se],
            'event':'At least one target suit card in two draws, not winning equity'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--monte-carlo',action='store_true');args=parser.parse_args()
    results=exact_results()
    if args.monte_carlo:results['monte_carlo']=monte_carlo()
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()

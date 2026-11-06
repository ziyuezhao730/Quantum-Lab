weights: T1=1 T2=2 T3=3
proficiency: T1=0.8 T2=0.2 T3=0.4
budget: 90 mins

first block vals:
T1 
- 1*(1-0.8) = 0.2
T2
- 1*(1-0.2) = 0.8
T3
- 1*(1-0.4) = 0.6

second block vals:
0.1
0.4
0.3

best allocs is t1=0, t2=60, t3=30
utility being 0.8+0.4+0.6=1.8, using all 90 mins

solver checks 27 allocations (the entire permutation)
tying utility prefers fewer blocks
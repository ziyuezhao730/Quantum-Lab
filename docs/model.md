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

r2 cost model:
bit order: x11,x12,x21,x22,x31,x32,y0,y1,y2
first 6 bits select study blocks
slack = y0+2*y1+4*y2
b = budget_minutes//30
a = weight*(1-proficiency)
p = 1+1.5*sum(a)
energy = -util + p*(selected+slack-b)^2 + p*sum(second*(1-first))

binary_energy: direct formula
build_binary_model: constant, linear, pair coeffs
binary_to_ising: z=(1-Z)/2, keep offset
ising_energy: 0 maps to +1, 1 maps to -1
pairs stored once

decode_bits: check slack, block order, time budget
invalid samples stay invalid
filter them before making a PlanResult
reverse qiskit count strings before decoding

checks: python3 -m pytest evidence/risi/check_quantum_model.py -q
covers 0, 3, 6 blocks; empty, optimal and invalid plans
checks offset, bit order, partial budget and nonunit weights
invalid-order example: -1.5+3.4 = 1.9
ai-assisted self-checks, no independent review or qiskit run yet

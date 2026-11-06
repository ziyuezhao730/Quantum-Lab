session model v2 - user-requested scope change, #41

app - up to 24 hours, 15-minute study blocks, breaks count toward budget.
45 minutes of work followed by 15-minute breaks, no required break after final work.
10 hours - 450 study minutes, 135 break minutes, 15 spare minutes.

exact allocation
priority a = reviewed weight * (1 - initial score).
nth 15-minute block has value a/n. utility is the sum of those values.
each topic has decreasing marginal value, blocks have equal cost.
choosing the largest remaining marginal value therefore gives the exact allocation
for this specific separable model. tests compare against independent enumeration.
fully proficient topics get no exact allocation. two questions are still a coarse signal.
this is a heuristic priority objective, not predicted learning.

schedule
allocations determine topic time. timeline rotates subjects between focus periods
when another topic needs time. 15-minute event records keep accounting exact;
ui groups consecutive same-topic events into readable focus cards.

compact quantum encoding
use the maximum useful study capacity s, including its required breaks.
store T1 block count in one binary register, T2 in another.
T3 = s - T1 - T2, reject negative T3. no additional slack register needed.
width = max(1, ceil(log2(s+1))), total qubits = 2*width.
10 hours needs s=30, two 5-bit registers, 10 qubits.
24 hours needs at most two 7-bit registers, 14 qubits.
if all priorities are zero, s=0 so exact & quantum use empty study plans.

the energy table gives valid counts negative harmonic utility.
invalid counts receive 1 + sum(a)*H_s, greater than any possible utility.
this model is not quadratic, so the new simulator applies its diagonal cost
phase directly, rather than pretending it is the old nine-qubit ising operator.
start in equal superposition, multiply each amplitude by exp(-i*gamma*energy),
then apply the standard x mixer using rx(2*beta).
optimize expected energy with one start, seed 7, p=1, at most 30 evaluations.
sample 1024 times, decode & choose best actually sampled feasible plan.
no exact answer is inserted into quantum output.

the simulator explicitly stores amplitudes & an energy table. this is a small
classical simulation, not hardware execution or evidence of speedup.

versioning
schema 1 - original 30-minute / 180-minute / nine-qubit experiment, unchanged.
schema 2 - new 15-minute, break-aware, long-session app export.
quantum_demo --profile dispatches on schema version. never reinterpret schema 1.
original r4 evidence remains a historical run of the original model.

files
sessions.py - capacity, harmonic value, exact allocation & timeline.
session_quantum.py - count encoding, diagonal qaoa simulation & comparison.
study_inputs.py - one-question dialog, answers in session memory only.
dashboard.py - theme, focus timeline & practice cards.
app.py - tabs, settings, export & same-session quantum comparison.

checks - 169 passed, no skips in the relevant combined suite.
real browser - stepped diagnostic, ten-hour plan, separate practice tab,
schema-2 profile download & long-session quantum comparison verified.
independent human review, rehearsal & event submission remain separate tasks.

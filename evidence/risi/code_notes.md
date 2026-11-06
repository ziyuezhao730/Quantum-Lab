r2 & r3 - code notes

project flow

fictional choices -> alex's scorer -> validated snapshot -> exact & qaoa -> report

r1 found the exact answer by checking 27 allocations.
r2 expresses that same problem as an energy. valid better plans have lower energy.
r3 uses the qaoa library circuit to sample candidate plans. it can return worse answers.
r4 needs the profile comparison, evidence tied to committed code & release review.
the command already saves comparison data, but this run used uncommitted r3 code.

quantum terms

qubit - a quantum system measured as 0 or 1. the simulator stores its amplitudes.
amplitude - a complex value whose squared magnitude gives measurement probability.
statevector - all amplitudes for this circuit. 9 qubits need 2**9 = 512 entries.
this describes a distribution over 512 bitstrings, not 512 answers you can read at once.
operator - a mathematical rule for scoring a state. ours assigns an energy to each bitstring.
z - operator with eigenvalue +1 on bit 0, -1 on bit 1.
zz - product of two z values, representing an interaction between two bits.
hamiltonian - the energy operator, our collection of z & zz terms.
ansatz - a circuit template with adjustable angles.
p=1 - one cost layer & one mixer layer, controlled by gamma & beta.
cost layer - changes phases according to the energy operator.
mixer - changes amplitudes so different candidates can interfere.
interference - amplitudes combine, raising some measurement probabilities & lowering others.
shot - one sampled measurement, yielding one nine-bit candidate.
expectation - probability-weighted average energy, not energy of the best candidate.
classical optimizer - changes the two angles to try lowering that average.
none of this guarantees a better allocation than the exact solver.

files

src/contracts.py - shared validated records, used by both solvers
src/intelligence/assess.py - answer ids to topic scores
src/intelligence/pipeline.py - course loading & score/budget snapshot with actual weights
src/optimizer/model.py - utilities, constraints, binary & ising calculations
src/optimizer/classical.py - exact reference, unchanged by r3
src/optimizer/quantum_demo.py - operator, circuit, optimization, sampling & report
export_fictional_profile.py - call the real scoring/export path with reviewed fictional answers
check_quantum_model.py - r2 self-checks using hand-calculated energies
check_qaoa.py - operator energies, tie rules, failed sampling & saved-report audit
qaoa_run.json - actual measurements, trace, settings, inputs & results
requirements-qaoa.txt - versions used by this experiment, not the team's shared dependency lock

r2 - model.py

BIT_ORDER fixes the meaning of each position. changing it changes the problem.
_check_bits checks 9 actual integer bits. booleans are deliberately rejected.
_profile_priorities checks topic keys & reuses the same w*(1-p) rule as exact.

binary_energy

vals - the three priorities
penalty - 1+1.5*sum(vals), larger than total possible utility
blocks - integer division by 30, so a leftover partial block stays unused
first, second - read each topic's pair from the six study bits
util += val*first + .5*val*second - supplied diminishing-return objective
bad_order += second*(1-first) - adds 1 only for a second block without its first
slack - last three bits represent unused blocks with weights 1,2,4
budget_diff - selected+slack-budget, must be zero
return - negative utility plus penalties, so minimizing favors valuable valid plans

build_binary_model

counts - each bit's contribution to selected+slack
values - first/second utility for each topic, zero utility for slack
linear coeff - p*c_j**2 - 2*p*b*c_j - value_j
this comes from expanding p*(sum(c*z)-b)**2, using z**2=z for binary bits
second-block linear term gets +p from p*second*(1-first)
pair coeff - 2*p*c_j*c_k, minus p for each same-topic first/second pair
j<k stores each interaction once, avoiding double counting
constant - p*b**2, needed for energy equality

polynomial_energy

constant + each linear coeff*bit + each pair coeff*bit_j*bit_k
this evaluates the expanded formula, independently of the original expression

binary_to_ising

z=(1-Z)/2 substitutes bits with z-operator eigenvalues
linear starts at -L/2
constant starts at C+sum(L)/2
each binary pair Q*z_j*z_k becomes Q*(1-Z_j-Z_k+Z_j*Z_k)/4
coupling=Q/4 therefore adds to offset & zz, subtracts from both z coefficients
keep offset even though a constant does not change which answer minimizes energy

ising_energy

spins=1-2*bit gives +1 or -1
sum offset, single-spin terms & two-spin interactions
known cases check this equals both earlier energy expressions

decode_bits

allocs - 30*(first+second) for each topic
util - score the actual sampled bits, not a substituted classical plan
second>first - flag invalid ordering
selected+slack must equal floor(budget/30), even if displayed minutes fit
is_feasible also checks the displayed allocation fits time constraints
feasible=not warnings means all these checks passed
negative unused time is possible for invalid samples, discard before presenting a successful plan

qiskit_bitstring_to_bits

qiskit displays the highest-index qubit on the left
reversed(bitstr) restores the index order used by our formula

r3 - quantum_demo.py

imports

argparse - command-line options
json - saved profile & report
subprocess - read source commit & working-tree status
datetime/timezone - unambiguous utc run timestamp
version - actual installed package versions
Path - file paths without hand-building separator strings
perf_counter - elapsed durations
numpy - reproducible initial angles
QAOAAnsatz - supplied circuit template
SparsePauliOp - compact sum of operator terms
Statevector - local ideal simulation
minimize - scipy's angle optimizer
validate_snapshot - reuse alex's input validation
solve_plan - exact reference on the same inputs
model imports - reuse r2 math & decoder, no separate scoring formula

settings

SEED=7 - repeatable initial angles & final sampling
SHOTS=1024 - final measurement count
MAX_EVALS=30 - objective call budget
REF - adapted ibm tutorial
ROOT=Path(__file__).resolve().parents[2] - repository root from this module location

load_profile

Path(path).read_text() reads exported json
json.loads turns text into a dictionary
validate_snapshot returns the shared validated ProfileSnapshot

cost_operator

('Z',[j],coeff) places a single z operator on qubit j
('ZZ',[j,k],coeff) places a z interaction on those two qubits
from_sparse_list avoids manually reversing pauli label strings
num_qubits=9 retains all nine qubits
simplify combines repeated terms & removes negligible coefficients
return op, offset keeps identity energy separate from circuit evolution

select_sample

best=None means no valid candidate found yet
qiskit_bitstring_to_bits reverses displayed count strings
decode_bits checks ordering, slack & budget
feasible_shots += count counts measurements, not distinct candidate strings
mins follows T1,T2,T3, so dictionary insertion order cannot change ties
tie=(-used,*mins) favors fewer blocks, then earlier topics
diff compares utility with tolerance 1e-12
skip worse utility, or an equal-utility candidate without a better tie key
best stores only a feasible candidate that actually appeared in counts
rate divides feasible measurements by all measurements
if none are feasible, best & bits stay None, no exact fallback

run_qaoa

validate_snapshot checks profile before starting model work
start=perf_counter starts timing before coefficient/operator construction
model_copy changes solver choice on a new request, leaving original profile intact
build_binary_model -> binary_to_ising -> cost_operator uses r2 as the source of truth
QAOAAnsatz(...reps=1,flatten=True) reuses library initial state & mixer
flatten avoids nested circuit overhead, not a different algorithm
params=tuple(circuit.parameters) records actual parameter order
rng=default_rng(7) makes a local reproducible random generator
uniform(0,pi,len(params)) creates one starting vector, not multiple attempts
trace records each objective call for the evaluation audit

objective

zip(params,angles) pairs each library parameter with its current value
assign_parameters binds those values to the circuit
Statevector.from_instruction simulates the bound circuit
state.expectation_value(op).real + offset gives full expected energy
float converts the numeric result to a json-friendly python float
trace appends angles & energy so evaluation count can be checked
return energy lets scipy decide its next angle values

minimize

method='COBYLA' uses a derivative-free classical optimizer
maxiter=30 means at most 30 objective evaluations for this method
disp=False suppresses optimizer printouts
result.x holds the best returned angles, result.fun its expected energy
hitting the cap can set success=False even when usable samples exist
we preserve that status rather than claiming convergence

final sampling

bind result.x, simulate once more, then seed the measurement sampler
sample_counts(1024) draws 1024 candidates from the final probability distribution
this final simulation is not an extra optimizer objective evaluation
int(val) makes sampled counts serialize reliably
select_sample filters invalid results & chooses best sampled feasible utility
elapsed includes construction, optimization, final sampling & decoding
raw_best_utility=None if sampling fails, otherwise sampled utility
counts & trace let the saved result be audited without running qaoa again

compare

validate original snapshot, copy request to exact without changing scores/weights/budget
solve_plan computes the exact reference, run_qaoa gets the sampled result
rev-parse HEAD records current source commit
status --porcelain detects uncommitted modifications, never hides them
capture_output=True reads git output without printing it
check=True raises if git fails instead of inventing source provenance
model_dump(mode='json') serializes the full validated profile & exact result
version(name) records installed versions
absolute gap is abs(exact utility - sampled utility), None on sampling failure
limitations state single-profile simulation scope & dirty-code status

main

--profile is required, --output defaults to ignored runtime storage
parse_args turns command-line strings into the configured values & Path objects
compare(load_profile(...)) validates then runs both solvers
parser.exit(1,...) reports invalid files/data as a failed command
mkdir(parents=True,exist_ok=True) creates missing output folders
json.dumps(...allow_nan=False) rejects non-finite report numbers
prints show actual utilities, feasible rate, evaluation count & report location
return 1 when no feasible sample exists, otherwise 0
raise SystemExit(main()) passes that status back to the terminal

export_fictional_profile.py

root is located from the script, not the caller's current directory
load first reviewed fictional response set & real course
score_diagnostic checks submitted choice ids against the reviewed keys
PlanRequest uses computed scores, not the fixture's expected scores
make_snapshot derives actual weights from assessment counts
write validated profile json to runtime/student_profile.json
this is a production-pipeline file export, not a claimed streamlit download

checks

operator basis-state energies match the direct formula for known valid/invalid inputs
sample tests deliberately give an invalid candidate most shots
that confirms frequency cannot override feasibility or the utility tie rule
no-feasible test requires None instead of an exact fallback
saved-run audit recomputes the reference & decodes saved counts
it checks 9 qubits, p=1, seed 7, 1024 shots & no more than 30 objective calls
these are self-checks, not an independent review

actual run

exact allocs - t1=0, t2=60, t3=30, util=1.4166666666666665
sample allocs - t1=0, t2=30, t3=0, util=0.6666666666666666
gap - .75
feasible shots - 86/1024
optimizer stopped at 30 evaluations, did not converge
this run found valid samples but did worse than exact
one run cannot establish reliability, hardware speed, quantum advantage or learning gains

commands

source .venv/bin/activate
python3 -m pytest tests/ evidence/risi/check_quantum_model.py evidence/risi/check_qaoa.py -q
python3 -m evidence.risi.export_fictional_profile
python3 -m src.optimizer.quantum_demo --profile runtime/student_profile.json

the last command runs a new experiment. reading qaoa_run.json only replays saved evidence.
commit source before rerunning if the next evidence must point to committed code.

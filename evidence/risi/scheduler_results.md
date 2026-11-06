scheduler comparison - fixed fictional examples

27 runs - three profiles, 12/15/18 session choices, seeds 7/11/23
p=1, at most 30 evaluations, 1024 samples per run
source - 3dfb985, clean tree during recorded runs

- feasible sampled schedule found in 27/27 runs
- mean sampled/exact score - 85.1%
- exact score matched in 4/27 runs
- mean feasible-shot rate - 8.2%
- earlier uniform-start qaoa mean feasible-shot rate - 2.8%
- example mixed-gaps, 18 choices - exact 12.815, greedy 10.936

exact solves the small constrained instance. qaoa is a local simulation comparison.
all reported runs retained, no hardware speedup or learning-gain result measured.
new checks ran locally, no new checker files added for this scheduler.

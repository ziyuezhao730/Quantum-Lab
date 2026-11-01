# StudyPack Five Day Delivery Guide

Daily schedule communication and Git workflow

Work within ninety minutes per person per night. The proposed project dates are Monday November 2 through Friday November 6 2026, in Waterloo and Toronto local time. Move the dates together if the actual event window differs; the day order and cutoffs matter more than these provisional calendar dates.

## 1 Evening routine

| Time | Activity | Rule |
| --- | --- | --- |
| 5:30 to 7:30 PM | Optional Qiskit lecture | No project dependency requires attendance. Alex and Risi tentatively attend Tuesday November 3. |
| 8:00 to 9:00 PM | Core work and buffer | Aim for one forty-five-minute outcome; keep fifteen minutes for setup, debugging, or explanation. |
| 9:00 to 9:15 PM | Check and integrate | Run the assigned check, review one small PR, and merge approved work in order. |
| 9:15 to 9:30 PM | Nightly stand-up | Fifteen minutes total. Record blockers and next actions, then stop. |

The Tuesday lecture adds two hours for its attendees; it is not included in the ninety-minute project budget. Tuesday's work uses the existing sample interfaces, so Charlie and Hank can continue independently. Any useful lecture insight becomes a short note in the regular stand-up, with no separate debrief or homework.

## 2 Five day checkpoints

| Day | Team result by stand-up | Individual outputs |
| --- | --- | --- |
| 1 Monday Nov 2 | V0 and schema freeze | Risi allocator first pass; Alex contracts/JSON; Charlie inputs; Hank baseline/data. |
| 2 Tuesday Nov 3 | V1 first pass and fixture freeze | Risi exact checks; Alex ranking; Charlie practice flow; Hank reviewed bank/counts and prepared PDF. |
| 3 Wednesday Nov 4 | V1 checked and quantum adaptation started | Risi adapts a library example; Alex prepared-format extraction; Charlie state; Hank smoke/query checks. |
| 4 Thursday Nov 5 | Core V2 candidate and feature freeze at 9 PM | Risi one fixed quantum report; Alex pipeline checks; Charlie core UI fixes; Hank clean-clone check. |
| 5 Friday Nov 6 | V2.1 release and demo backup | Fix only release blockers; rehearse; capture evidence; tag the tested commit. |

Plan 225 minutes of focused core work, seventy-five minutes of implementation buffer, seventy-five minutes of checks/review, and seventy-five minutes of stand-ups per person. Total is seven and a half hours each. There is no separate learning phase and no expected work after 9:30 PM. If a core task overruns, stop, report the blocker, and adjust the next slice. Optional items never become someone else's obligation. No estimate is a guarantee of equal effort.

## 3 Communication and decisions

Use one team channel, one issue board, and the repository. Board stages are Backlog, Doing, Review, Done. Each issue has one owner, a day, requirement, output, and check. Split work into reviewable evening slices.

### Fifteen minute stand up

Give each person two minutes: what runs now with an evidence link, what is blocked, and the next small action. Use the remaining seven minutes for one integrated demonstration, the merge queue, and decisions. Debugging continues in the next scheduled block, not inside the report.

Rotate facilitator: Hank Monday, Charlie Tuesday, Alex Wednesday, Risi Thursday, Hank Friday. The facilitator enforces the timer. Hank records shared decisions in docs/decisions.md; each owner updates only their own stand-up note, which prevents four people editing one log.

After ten stuck minutes, post the input/error, expected and actual behavior, attempts, and person needed. Responses may be asynchronous. If absent, post an update before 9 PM with a handoff.

### Decision and scope rules

Owners choose internal details. Coordinate contract, dependency, and shared-file changes in an issue with affected owners. Replace work of similar effort before increasing core scope.

- If setup is blocked after fifteen minutes on Day 1, use one working development environment for the demo and continue with component examples; Hank resolves installation during the next allocated work slice.
- If the classical flow is behind on Day 2, use Day 3's core buffer before starting any optional work. Keep reviewed JSON as the app input.
- If extraction is blocked, support only the supplied marked exercise PDF with a separate script. Do not expand formats, add AI tagging, or build an upload editor to solve that blocker.
- If quantum adaptation is blocked, reuse the documented library ansatz for the one fixed fixture. Live app integration, custom gates, and larger benchmarks are optional and must not consume the core recovery time.
- At 9 PM on Day 4, freeze features. A complete core V2 needs the separate fixed quantum run, not a quantum button. If that core run fails, label the release V1 and state the actual status.
- On Day 5, protect the working core and recording. Optional items may remain unclaimed or deferred without affecting completion.

The optional backlog is Document 01 section 10. A volunteer claims one issue only after core checks pass, states a personal time limit, and coordinates affected files. It stays in a separate PR. Review may wait until the core is ready; no other member owes extra time. Unfinished optional work stays out of the release, and no optional item is a release gate.

### Pull request description

```text
Requirement and issue:
Implemented by:    Checked by:    Reviewed by:
Behavior before and after:
Input/output example:
Checks run and actual result:
Limitation or deferred work:
AI assistance by contributor: what it produced; what I checked/changed.
```

Everyone should be able to explain their own completed change using its input, output, verification result, and one limitation.

## 4 Repository layout and edit boundaries

Create a standalone repository for this hackathon. Use one shared origin and one main branch. Each person makes their own clone. There is no course upstream remote and no need to copy the SE101 application or its database setup.

```text
studypack/
  app.py                          Charlie
  src/
    contracts.py                  Alex
    intelligence/                 Alex
      pdf_extract.py  validate.py  pipeline.py  rank.py
    optimizer/                    Risi
      model.py  classical.py  quantum_demo.py
    ui/                           Charlie
      inputs.py  results.py
  tests/
    test_optimizer.py             Hank
    test_intelligence.py          Risi
    test_fixtures.py               Charlie
    check_ui.md                   Alex
  data/demo/                      Hank
    course.json  oracle.json  retrieval_cases.json
    exercises.pdf
  scripts/smoke.py                 Hank
  docs/
    model.md                      Risi
    pipeline.md                   Alex
    ui.md                         Charlie
    decisions.md  delivery/       Hank
    standups/                     one file per person
  evidence/                       one folder per person
  runtime/                        ignored uploads and cache
  README.md  HOW-TO-RUN.md         Hank
  requirements.in  requirements.txt  .gitignore   Hank
```

Add empty __init__.py files in src/ and each Python subfolder during baseline setup. tests/ can remain a plain folder. Put no notebooks or generated results in a shared file; export a useful small artifact into your own evidence folder.

If a change needs someone else's file, open an issue comment with the proposed change. Its owner edits it or explicitly hands it over for that PR. Alex alone edits contracts; Hank alone edits dependencies, root instructions, and shared decisions. Reviewers comment rather than modifying the author's branch. Testers use their assigned check file in the implementation PR, following section 7.

Keep implementation changes under roughly two hundred changed lines when practical, excluding fixture data. Never have two active PRs modifying the same file without an agreed order. New work branches from updated main. Optional modules and tests are created only by a volunteer; the core never imports or requires them.

## 5 Repository and environment setup

These are commands to run when implementation starts; this planning pack does not create or publish a repository. Use GitHub pull requests or GitLab merge requests consistently. Both use the same local commands below. Have an empty remote named studypack ready, and replace REPO_URL with its actual clone URL. Never paste account tokens into commands or files.

### One time bootstrap by Hank

```bash
mkdir studypack
cd studypack
git init -b main
git remote add origin REPO_URL
mkdir -p src/intelligence src/optimizer src/ui tests data/demo
mkdir -p scripts docs/standups docs/delivery evidence runtime
touch src/__init__.py src/intelligence/__init__.py
touch src/optimizer/__init__.py src/ui/__init__.py
```

These commands assume a completely empty remote with no initial README. In an editor, create the named module placeholders, README.md, HOW-TO-RUN.md, and requirements.in. The first dependency list is streamlit, pypdf, pydantic, numpy, scipy, scikit-learn, qiskit, and pytest, one per line. Use Python 3.12 on all four machines if available; agree one working version on Day 1 and record it.

Create .gitignore before staging anything:

```gitignore
.venv/
__pycache__/
.pytest_cache/
.env
.env.*
!.env.example
runtime/
.DS_Store
```

### Install and record a working environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.in
python -m pip freeze > requirements.txt
git status --short
git add .gitignore README.md HOW-TO-RUN.md requirements.in
git add requirements.txt src tests data scripts docs evidence
git diff --cached --stat
git commit -m "Create shared project skeleton"
git push -u origin main
```

Only Hank updates the lock file, from this clean project environment. On Windows PowerShell use py -3.12 -m venv .venv, then .\.venv\Scripts\Activate.ps1; create the same folders/files in the editor instead of the Unix mkdir/touch commands. Other commands use python after activation. If activation is unavailable, invoke the environment's Python executable directly; do not change machine security settings for this project.

All other members then clone REPO_URL, create the same environment, and install with python -m pip install -r requirements.txt. Do not regenerate the lock file in individual component branches. Installation time belongs to the Day 1 budget.

## 6 Daily branch and review workflow

Start each new issue with a clean working tree. Example branch names are risi/d2-exact-checks, alex/d2-ranking, charlie/d2-practice-view, and hank/d2-demo-data. Use one branch per small issue, not one permanent branch for the whole hackathon.

```bash
git status
git switch main
git pull --ff-only origin main
git switch -c risi/d2-exact-checks
# Edit only the agreed files, then run relevant checks.
python -m pytest tests/test_optimizer.py -q
git diff --check
git diff -- src/optimizer/model.py
git add src/optimizer/model.py docs/model.md
git diff --cached
git commit -m "Check study budget allocation (#ISSUE)"
git push -u origin risi/d2-exact-checks
```

Replace the branch, filenames, test, and issue marker with the actual task. Check only test files that exist; a missing test is unfinished verification, not a pass. Inspect staged changes before committing. Avoid git add . so unrelated work and uploads do not slip in.

Open a pull request in the hosting site's interface, target main, and paste the description from section 3. The assigned checker adds tests or the manual procedure to the same PR using section 7. A required check must pass before the implementation is accepted; do not merge code on an unverified claim.

### Bring main into an existing branch

```bash
git status
# Commit the current coherent work before merging.
git fetch origin
git merge origin/main
# Resolve conflicts if any, then rerun relevant checks.
git push
```

Use merge instead of rebase for this short beginner project; no force push is needed. If the latest main changes behavior, the reviewer checks the updated PR again. Do not rename or move common files while component branches are active.

After a PR is merged:

```bash
git switch main
git pull --ff-only origin main
git log --oneline --first-parent -5
git branch -d risi/d2-exact-checks
```

Delete the local branch only after confirming the PR is merged. If Git refuses deletion, keep it and check the history; do not force-delete it. The next task gets a new branch from main.

## 7 Independent checks and merge queue

Use one PR for a component slice and its checks. The implementation author owns the feature files; the assigned checker owns only the named test file or manual-check document. Coordinate a short turn to push so their commits do not race. Both contributions remain visible in the PR history.

The checker begins with a clean working tree and joins the already-pushed feature branch. This is participation in the same issue, rather than starting a new feature from someone else's branch. Example for Hank checking Risi's work:

```bash
git fetch origin
git switch --track origin/risi/d2-exact-checks
# Edit only tests/test_optimizer.py.
python -m pytest tests/test_optimizer.py -q
git add tests/test_optimizer.py
git commit -m "Verify known allocation examples (#ISSUE)"
git push origin HEAD
```

If that local branch already exists, switch to it and use git pull --ff-only origin risi/d2-exact-checks before editing. The implementation author also pulls the branch before making further changes. If a push is rejected because both people committed, run git fetch origin, inspect the changes together, then git merge origin/risi/d2-exact-checks on that feature branch. Resolve conflicts and rerun checks before pushing; do not force push. The third person reviews the implementation and the check together.

For the UI, Alex records the manual procedure and actual outcomes in tests/check_ui.md on Charlie's PR. For fixture work, Charlie adds tests/test_fixtures.py on Hank's PR. Reviewers comment rather than making uncoordinated edits. No one approves their own implementation.

### Merge order and responsibility

At the check block, use this order when dependencies are waiting: fixtures and contracts, decision engine and intelligence modules, interface wiring, then release notes. A stub may land in V0 only with a visible placeholder label and an issue for the real behavior.

Hank maintains the queue, but does not review or approve their own work. For Hank's PRs, Risi performs the merge after the assigned independent check and review. Use the hosting site's “create a merge commit” option, preserving the issue grouping; do not squash or fast-forward. Merge one PR, then update and check the next. No direct feature commits to main after the baseline.

If a later commit changes checked behavior, rerun the affected checks and obtain review of that change before merging. At stand-up, report the actual integrated state; an open PR does not count as delivered behavior.

## 8 Conflicts checks and release

Before merging, commit or otherwise preserve all work and check git status. If the incoming merge conflicts, identify the files first:

```bash
git status
git diff --name-only --diff-filter=U
```

Contact each conflicting file's owner. In an editor, combine the intended changes and remove the <<<<<<<, =======, and >>>>>>> markers. Do not choose “ours” or “theirs” for a whole file without reading both changes. Then stage the explicit resolved files, run the relevant checks, commit the merge, and push. Example:

```bash
git add src/optimizer/model.py
python -m pytest tests/test_optimizer.py -q
git diff --check
git commit -m "Merge main and resolve model conflict"
git push
```

To stop an unresolved merge and return to the pre-merge branch, use git merge --abort. This is why the working tree must be clean first. Avoid reset --hard, force push, or deleting files to make a conflict disappear. If a merged PR breaks main, preserve evidence and revert its merge through a reviewed repair PR; do not rewrite shared history.

### Checks at the release candidate

From the repository root in the activated environment:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/smoke.py
python -m streamlit run app.py
```

The team implements these checks. Complete the manual UI procedure. In a second activated terminal, run python -m src.optimizer.quantum_demo for the fixed experiment. Optional benchmarks are not acceptance requirements. Hank records commands, outcomes, commit, Python version, and limitations in docs/delivery/results.md.

On Thursday, Charlie or Hank repeats setup in a second clone or clean environment. On Friday, record the working route before attempting last fixes. Confirm the event's submission deadline, demo length, repository visibility, and AI disclosure rules in Day 1's existing coordination block; place the confirmed details in the delivery issue. The dates here are planning dates, not an assertion of the organizer's deadline.

### Tag the tested main commit

After all final PRs are merged, repeat the release checks on current main. Check that it is the reviewed commit, then tag:

```bash
git switch main
git pull --ff-only origin main
git status
git log -1 --oneline
git tag -a v2.1-demo -m "Verified five day demo release"
git push origin v2.1-demo
```

The tag denotes core completion with no optional quota. Use v1.0-demo if the core quantum experiment is incomplete. Do not move a release tag. Keep the recording and saved quantum inputs, timestamp, and replay label.

Git reference for merge and abort behavior: https://git-scm.com/docs/git-merge

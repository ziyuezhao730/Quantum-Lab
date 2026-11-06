"""fixed fictional scheduling cases, three seeds each"""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from src.intelligence.pipeline import load_course
from src.intelligence.assess import score_diagnostic
from src.optimizer.sessions import make_study_snapshot
from src.optimizer.scheduler import make_options,compare_schedule


def main():
    parser=argparse.ArgumentParser(description="compare schedulers on fixed fictional cases")
    parser.add_argument("--output",type=Path,default=ROOT/"runtime/scheduler_benchmark.json")
    args=parser.parse_args()
    course=load_course(ROOT/"data/demo/course.json")
    profiles={"weak_integrals":{"T1":1.,"T2":0.,"T3":.5},"mixed_gaps":{"T1":.5,"T2":0.,"T3":0.},"weak_derivatives":{"T1":0.,"T2":.5,"T3":1.}}
    results=[]
    examples=[]
    for label,target in profiles.items():
        answers={}
        used=dict.fromkeys(target,0)
        for q in course.questions:
            if q.purpose!="diagnostic":
                continue
            correct=used[q.topic_id]<int(2*target[q.topic_id])
            answers[q.question_id]=q.correct_choice if correct else next(c for c in q.choices if c!=q.correct_choice)
            used[q.topic_id]+=1
        scores=score_diagnostic(course,answers).proficiency
        for size,budget in ((12,240),(15,360),(18,600)):
            snapshot=make_options(make_study_snapshot(course,scores,budget))
            snapshot=snapshot.model_copy(update={"sessions":snapshot.sessions[:size]})
            examples.append({"case":f"{label}_{size}","answers":answers,"profile":snapshot.model_dump(mode="json")})
            for seed in (7,11,23):
                report=compare_schedule(snapshot,seed=seed)
                q=report["quantum"]
                results.append({"case":f"{label}_{size}","choices":size,"budget_minutes":budget,"seed":seed,"exact":report["exact"]["utility"],"greedy":report["greedy"]["utility"],"qaoa":q["raw_best_utility"],"uniform":report["uniform"]["raw_best_utility"],"feasible_rate":q["feasible_shot_rate"],"uniform_feasible_rate":report["uniform"]["feasible_shot_rate"],"gap":report["absolute_utility_gap"],"exact_ms":report["exact"]["elapsed_ms"],"qaoa_ms":q["elapsed_ms"],"evaluations":q["objective_evaluations"],"code_commit":report["code_commit"],"working_tree_dirty":report["working_tree_dirty"]})
                print(f"{label} {size} seed {seed} - exact {report['exact']['utility']:.3f}, greedy {report['greedy']['utility']:.3f}, qaoa {q['raw_best_utility']}, feasible {q['feasible_shot_rate']:.1%}",flush=True)
                if label=="mixed_gaps" and size==18 and seed==7:
                    full=args.output.with_name("scheduler_example.json")
                    full.parent.mkdir(parents=True,exist_ok=True)
                    full.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({"model_version":3,"cases":examples,"settings":{"seeds":[7,11,23],"p":1,"max_evaluations":30,"shots":1024},"results":results},indent=2,allow_nan=False)+"\n")


if __name__=="__main__":
    main()

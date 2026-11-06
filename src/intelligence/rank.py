"""topic-filtered practice retrieval, no diagnostic items"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.contracts import PracticeItem


def select_questions(course, plan, proficiency):
    topics={topic.topic_id:topic for topic in course.topics}
    result=[]
    seen=set()
    ordered=sorted(plan.allocations, key=lambda t:(-plan.allocations[t],t))
    for topic_id in ordered:
        if plan.allocations[topic_id]==0:
            continue
        topic=topics[topic_id]
        candidates=sorted((q for q in course.questions if q.topic_id==topic_id and q.purpose=="practice" and q.review_status=="approved"),key=lambda q:q.question_id)
        if not candidates:
            continue
        query=" ".join([topic.name]+[e.excerpt for e in topic.evidence])
        docs=[query]+[q.text for q in candidates]
        vectors=TfidfVectorizer(token_pattern=r"(?u)\b\w+\b|[^\w\s]").fit_transform(docs)
        similarities=cosine_similarity(vectors[0:1],vectors[1:]).ravel()
        score=proficiency[topic_id]
        target=1 if score<.4 else 2 if score<.7 else 3
        ranked=[]
        for q,similarity in zip(candidates,similarities):
            similarity=float(min(1,max(0,similarity)))
            match=int(q.difficulty==target)
            rank_score=.7*similarity+.3*match
            reason=f"topic {topic.name}, text match {similarity:.2f}, target difficulty {target}, difficulty match {'yes' if match else 'no'}"
            ranked.append((rank_score,q,reason))
        ranked.sort(key=lambda item:(-item[0],item[1].question_id))
        chosen=0
        for rank_score,q,reason in ranked:
            normalized=" ".join(q.text.casefold().split())
            if normalized in seen:
                continue
            seen.add(normalized)
            result.append(PracticeItem(question_id=q.question_id,score=rank_score,reason=reason))
            chosen+=1
            if chosen==2:
                break
    return result

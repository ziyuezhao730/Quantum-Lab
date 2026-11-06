# ExamAce — Hank's demo script (bilingual)

Four-minute demo, per docs/01_requirements.md section 9. Hank speaks twice:
opening (~45 s) and closing (~45 s). Everything else belongs to Charlie, Alex, Risi.

Speaking pace target: about 140 words per minute. Both parts are ~105 words,
which lands at roughly 45 seconds each with one breath between sentences.

---

## Part 1 — Opening (~45 s) / 开场

**English (read this on stage)**

> Hi everyone, I'm Hank. Here is the problem we started from. An exam is in two
> days. You have ninety minutes tonight and three topics to cover. Which one do
> you open first? Most students guess. We turn that guess into a calculation.
> You answer six diagnostic questions, two per topic. We score each topic from
> zero to one. You enter the minutes you actually have. Then we compute how to
> split them into thirty-minute blocks, thirty or sixty minutes per topic. The
> course is fictional: one calculus course, three topics, twelve reviewed
> questions. No real student data is used.

**中文（对照理解，不要念）**

> 大家好，我是 Hank。我们的出发点是一个很具体的问题：两天后考试，今晚你只有
> 九十分钟，三个主题都要复习，你先打开哪一个？大多数人是凭感觉猜。我们把这种
> 猜变成一个计算：你答六道诊断题（每个主题两道），我们给每个主题打一个 0 到 1
> 的分数；你再输入今晚真正有多少分钟。然后系统算出怎么把这些时间切成三十分钟
> 一块，每个主题分三十分钟还是六十分钟。这门课是虚构的：一门微积分课，三个
> 主题，十二道审核过的题。没有用任何真实学生的数据。

**动作提示**

- 说 "Here is the problem" 时停一拍，让评委把注意力从 PPT 转到你身上。
- 说到 "Most students guess" 时抬头看评委一秒，这是全场的钩子。
- 数字只说三个：九十、六、十二。不要临时加数字，容易卡。

---

## Part 2 — Closing (~45 s) / 收尾

**English (read this on stage)**

> Three things to close. First, what we submit is checked. The tests pass, every
> number traces back to reviewed data, and a clean clone reproduces the run.
> Second, the limits. Three topics, twelve questions, six multiple-choice
> answers. So a topic score is an initial impression, not mastery. We do not
> predict grades and we do not claim learning gains. There is no AI grading;
> answers are checked against a key. Third, the quantum part is a separate
> script that compares QAOA with the exact solver on one saved profile. We
> report it as a case study, not as an advantage. Thank you, questions welcome.

**中文（对照理解，不要念）**

> 收尾三件事。第一，我们交出来的东西是验过的：测试全绿，每个数字都能追回审核过
> 的数据，换一台干净机器能复现整条流程。第二，边界。三个主题、十二道题、六道
> 选择题，所以单个主题的分数只是"初步印象"，不代表掌握程度；我们不预测成绩，
> 也不声称提升了学习效果；没有 AI 判卷，答案是对着标准答案核的。第三，量子
> 部分是一个独立脚本，在同一份保存下来的学生档案上，把 QAOA 和精确解放在一起
> 比。我们把它当成一个个案研究，不声称量子优势。谢谢，欢迎提问。

**动作提示**

- 三件事用三根手指数出来（First / Second / Third），评委能跟上结构。
- "we do not claim learning gains" 这句要放慢、加重——这是最能加分的一句。
- 如果量子部分最终没合进主分支，删掉第三件事的最后两句，改成
  "Third, the quantum part is a separate experiment and we keep it out of the
  demo path." 然后直接说 Thank you。

---

## Likely questions (bilingual, 20 s each)

**Q1: Why only three topics and twelve questions?**
> Five days, four people, ninety minutes a night. We would rather ship a small
> system that is correct and explainable than a big one nobody can defend.
>
> 五天、四个人、每晚九十分钟。我们宁可交一个小而正确、讲得清的系统，也不交一个
> 大而谁都讲不清的。

**Q2: Is this AI grading?**
> No. Scoring is key-based, one point per correct choice. TF-IDF only decides
> which practice questions to show; it never marks an answer.
>
> 不是。判分是对答案键，答对一个给一分。TF-IDF 只决定推荐哪几道练习题，从不参与
> 判分。

**Q3: Does the quantum part help?**
> On one nine-qubit problem, QAOA gives a feasible plan and we report the gap to
> the exact answer. One simulation is a case study; it proves no speedup.
>
> 在一个九比特的问题上，QAOA 能给出可行方案，我们报告它和精确解的差距。一次
> 模拟只是个案研究，证明不了加速。

---

## Timing plan

| Who | Seconds | What |
| --- | --- | --- |
| Hank | 45 | problem + fictional course (Part 1) |
| Charlie | 60 | six answers, topic scores, snapshot download |
| Alex | 60 | one answer traced through scoring and retrieval |
| Risi | 60 | QAOA vs exact comparison, limits of a simulation |
| Hank | 45 | checked release + known scope (Part 2) |

Total 4 minutes plus transitions. If the demo runs long, cut Alex's second
student example first; never cut Hank's Part 2.

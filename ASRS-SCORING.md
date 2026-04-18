# ASRS-SCORING.md — Adult ADHD Self-Report Scale v1.1

## Overview

The Adult ADHD Self-Report Scale v1.1 (ASRS v1.1) was developed by Ronald C. Kessler and colleagues for the World Health Organization (WHO) as a validated screening instrument for adult ADHD. The full scale consists of 18 questions derived from the DSM-IV criteria for ADHD. **Part A (questions 1–6) is the clinically validated screening portion** — studies show these six questions are the most predictive of ADHD diagnosis. Part B (questions 7–18) is supplementary, collecting additional symptom data but is NOT used for diagnosis in Glorb. Only Part A scores determine the `hasADHD` flag.

---

## The 18 Questions (full text)

### Part A (Screening, Q1–Q6)

1. How often do you have trouble wrapping up the final details of a project, once the challenging parts have been done?
2. How often do you have difficulty getting things in order when you have to do a task that requires organization?
3. How often do you have problems remembering appointments or obligations?
4. When you have a task that requires a lot of thought, how often do you avoid or delay getting started?
5. How often do you fidget or squirm with your hands or feet when you have to sit down for a long time?
6. How often do you feel overly active and compelled to do things, like you were driven by a motor?

### Part B (Supplementary, Q7–Q18 — collected but not scored)

7. How often do you make careless mistakes when you have to work on a boring or difficult project?
8. How often do you have difficulty keeping your attention when you are doing boring or repetitive work?
9. How often do you have difficulty concentrating on what people say to you, even when they are speaking to you directly?
10. How often do you misplace or have difficulty finding things at home or at work?
11. How often are you distracted by activity or noise around you?
12. How often do you leave your seat in meetings or other situations in which you are expected to remain seated?
13. How often do you feel restless or fidgety?
14. How often do you have difficulty unwinding and relaxing when you have time to yourself?
15. How often do you find yourself talking too much when you are in social situations?
16. When you're in a conversation, how often do you find yourself finishing the sentences of the people you are talking to, before they can finish them themselves?
17. How often do you have difficulty waiting your turn in situations when turn taking is required?
18. How often do you interrupt others when they are busy?

---

## Scoring Algorithm (Part A Only)

The response scale maps dot index (0–4) to labels:

| Index | Label      |
|-------|------------|
| 0     | Never      |
| 1     | Rarely     |
| 2     | Sometimes  |
| 3     | Often      |
| 4     | Very Often |

### Positive thresholds for Part A:

- **Q1, Q2, Q3:** positive if answer ≥ 2 (Sometimes or higher)
- **Q4, Q5, Q6:** positive if answer ≥ 3 (Often or higher)

### Diagnosis rule:

```
hasADHD = (positiveCount >= 4)
```

where `positiveCount` = number of Q1–Q6 answers that meet their respective threshold.

### Example scoring function (JavaScript):

```js
function scoreASRS(asrsAnswers) {
  // asrsAnswers: int[18], values 0–4 (dot index)
  const thresholds = [2, 2, 2, 3, 3, 3]; // Q1–Q6
  let positiveCount = 0;
  for (let i = 0; i < 6; i++) {
    if (asrsAnswers[i] >= thresholds[i]) positiveCount++;
  }
  return positiveCount >= 4; // true = likely ADHD
}
```

---

## Implementation Notes

- `asrsAnswers` is stored as `int[18]` where each value is 0–4 (dot index)
- Only `asrsAnswers[0]` through `asrsAnswers[5]` (Q1–Q6) are evaluated for diagnosis
- `hasADHD` boolean is derived at questionnaire completion and written to store
- Full store schema: `{ userName: string, hasADHD: bool, asrsAnswers: int[18], onboardingComplete: bool }`
- Part B answers (indices 6–17) are persisted but not evaluated

---

## References

- Kessler RC, et al. "The World Health Organization Adult ADHD Self-Report Scale (ASRS)." *Psychological Medicine* (2005).
- ASRS v1.1 Symptom Checklist, WHO (2003).

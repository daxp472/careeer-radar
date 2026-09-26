# CareerRadar — Analysis & Readiness Engine

## 1. Deterministic Readiness Formula

The Readiness Engine computes candidate readiness purely through transparent mathematical calculation over verified market evidence.

### Candidate Proficiency Weights

| Level | Coverage Weight ($w_c$) |
|---|---|
| `beginner` | 0.25 |
| `known` | 0.50 |
| `intermediate` | 0.70 |
| `advanced` | 0.90 |
| `expert` | 1.00 |
| *missing* | 0.00 |

### Market Skill Importance

For each skill $i$ appearing in the market snapshot:
$$Importance_i = \text{FrequencyPct}_i \times \text{Weight}_{\text{role\_requirement}}$$

Where $\text{FrequencyPct}_i = \frac{\text{Jobs with Skill}_i}{\text{Total Jobs in Snapshot}} \times 100$

### Overall Readiness Score

$$\text{Readiness} = \frac{\sum (Importance_i \times Coverage_i)}{\sum Importance_i} \times 100$$

---

## 2. Skill Gap Classification

- **Matched**: Candidate has $\ge 0.70$ proficiency (`intermediate`, `advanced`, `expert`).
- **Weak**: Candidate has $\le 0.50$ proficiency (`beginner`, `known`).
- **Missing**: Candidate has no record for the skill ($Coverage = 0$).

## 3. Priority Scoring for Gaps

$$\text{PriorityScore} = \text{MarketFrequencyPct} \times (1.0 - \text{CandidateCoverage})$$

This surfaces high-demand skills that the candidate either lacks completely or is weak in as the highest priority action items.

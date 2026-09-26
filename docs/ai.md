# CareerRadar — AI Layer Integration

## 1. Principles

1. **AI is an explanatory enhancement layer, NOT the calculation engine.**
2. **Deterministic calculations must never be generated or altered by the LLM.**
3. **The LLM receives structured, verified evidence from PostgreSQL.**
4. **The LLM strictly explains the data and formulates structured learning action items.**

## 2. Evidence-Based Prompt Design

The backend constructs a strict JSON payload containing:
- Target Role & Location
- Sample count (Jobs analyzed)
- Top Market Skills & their calculated frequency percentages
- Candidate Matched, Weak, and Missing skill categories
- Computed deterministic readiness score

The LLM is prompted with strict guardrails:
- Never fabricate job market percentages.
- Never invent skills outside the market snapshot.
- Focus exclusively on explaining the gap rationale and recommending practical project-based learning steps.

import json
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.logging import logger

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class LLMClient:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.api_key = settings.LLM_API_KEY
        self.model_name = settings.LLM_MODEL or "gemini-1.5-flash"
        
        if self.provider == "gemini" and self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None

    async def generate_market_explanation(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send structured market evidence to LLM with strict instructions NOT to modify
        or invent numbers, but to produce high-impact evidence explanations and action plans.
        """
        if not self.model or self.provider == "mock":
            return self._generate_rule_based_explanation(evidence)

        prompt = f"""
You are the CareerRadar Market Intelligence AI.
Analyze the following structured evidence from a LIVE job market scan and provide a clear, encouraging, and highly specific explanation.

STRICT RULES:
1. Do NOT invent or alter any percentages or numbers.
2. The readiness score is deterministically {evidence.get('readiness_score')}%. Do NOT recalculate or contradict it.
3. Base your recommendations ONLY on the provided market demand frequencies and candidate gaps.
4. Provide structured JSON output with:
   - "summary": A 2-3 sentence overview explaining how well the candidate aligns with the analyzed {evidence.get('jobs_analyzed')} live jobs.
   - "action_items": A list of 3-5 prioritized recommendations. Each item must have:
       - "title": Actionable title (e.g., "Build a typed full-stack project with TypeScript & PostgreSQL")
       - "description": Why it matters based on market frequency, and exactly what to build/learn.
       - "skill_name": Target canonical skill
       - "priority": Integer (1 is highest)
       - "estimated_effort_hours": Realistic estimate in hours

STRUCTURED EVIDENCE:
Target Role: {evidence.get('target_role')}
Location: {evidence.get('location')}
Jobs Analyzed: {evidence.get('jobs_analyzed')}
Deterministic Readiness Score: {evidence.get('readiness_score')}%

Top Market Skills:
{json.dumps(evidence.get('market_skills', []), indent=2)}

Candidate Matched Skills:
{json.dumps(evidence.get('matched_skills', []), indent=2)}

Candidate Weak Skills:
{json.dumps(evidence.get('weak_skills', []), indent=2)}

Candidate Missing High-Demand Skills:
{json.dumps(evidence.get('missing_skills', []), indent=2)}

Return ONLY valid JSON matching this schema:
{{
  "summary": "...",
  "action_items": [
     {{
        "title": "...",
        "description": "...",
        "skill_name": "...",
        "priority": 1,
        "estimated_effort_hours": 15
     }}
  ]
}}
"""
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Handle potential markdown fence ```json
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            data = json.loads(text.strip())
            return data
        except Exception as e:
            logger.error(f"[LLM] Gemini generation failed ({e}); falling back to deterministic explanation generator.")
            return self._generate_rule_based_explanation(evidence)

    def _generate_rule_based_explanation(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        score = evidence.get("readiness_score", 0)
        jobs_count = evidence.get("jobs_analyzed", 0)
        role = evidence.get("target_role", "Developer")
        missing = evidence.get("missing_skills", [])
        weak = evidence.get("weak_skills", [])
        matched = evidence.get("matched_skills", [])

        top_missing_names = [m["name"] for m in missing[:3]]
        matched_names = [m["name"] for m in matched[:3]]

        summary = (
            f"Based on {jobs_count} live opportunities for {role}, you demonstrate a {score}% market alignment. "
            f"You have strong market coverage in {', '.join(matched_names) if matched_names else 'foundational skills'}. "
            f"Closing gaps in high-demand technologies like {', '.join(top_missing_names) if top_missing_names else 'cloud & deployment'} will maximize your hiring readiness."
        )

        action_items = []
        priority = 1
        for m in missing[:3]:
            action_items.append({
                "title": f"Master {m['name']} for Live Market Alignment",
                "description": f"{m['name']} appeared in {m.get('market_frequency_pct', 0)}% of analyzed {role} jobs. Build a hands-on production feature utilizing {m['name']}.",
                "skill_name": m["name"],
                "priority": priority,
                "estimated_effort_hours": 15
            })
            priority += 1

        for w in weak[:2]:
            action_items.append({
                "title": f"Elevate {w['name']} from Beginner to Intermediate",
                "description": f"Employers frequently test practical depth in {w['name']} (demand: {w.get('market_frequency_pct', 0)}%). Add test coverage or optimization to your existing projects.",
                "skill_name": w["name"],
                "priority": priority,
                "estimated_effort_hours": 10
            })
            priority += 1

        return {
            "summary": summary,
            "action_items": action_items
        }


llm_client = LLMClient()

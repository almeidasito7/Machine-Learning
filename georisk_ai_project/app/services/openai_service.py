from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def generate_narrative(data: dict) -> str:
    try:
        if not settings.openai_api_key:
            return _fallback(data)

        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        prompt = _build_prompt(data)

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": _system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=220,
        )

        content = response.choices[0].message.content
        if not content:
            return _fallback(data)

        return content.strip()

    except Exception as e:
        logger.warning(f"LLM generation failed: {e}")
        return _fallback(data)


def _system_prompt() -> str:
    return (
        "You are a geotechnical risk analyst. "
        "Use only the provided data. "
        "Be specific, concise, technical, and objective. "
        "Mention the most critical structures when applicable."
    )


def _build_prompt(data: dict) -> str:
    top_structures = data.get("top_structures", [])
    top_text = "\n".join(
        [
            f"- structure_id={s['structure_id']}, risk={s['avg_risk_score']:.4f}, "
            f"failure_probability={s['failure_probability']:.4f}, level={s['risk_level']}"
            for s in top_structures
        ]
    )

    return f"""
Geotechnical analysis summary

Total structures: {data.get("total_structures")}
High risk structures: {data.get("high_risk")}
Medium risk structures: {data.get("medium_risk")}
Low risk structures: {data.get("low_risk")}

Average risk score: {data.get("avg_risk_score")}
Average failure probability: {data.get("avg_failure_probability")}

Top critical structures:
{top_text if top_text else "- none"}

Generate a technical summary describing:
- overall risk posture
- whether there are concentrated critical structures
- whether failure probability appears homogeneous or uneven
- suggested operational attention level
""".strip()


def _fallback(data: dict) -> str:
    return (
        f"Analysis completed for {data.get('total_structures', 0)} structures. "
        f"High risk: {data.get('high_risk', 0)}, "
        f"medium risk: {data.get('medium_risk', 0)}, "
        f"low risk: {data.get('low_risk', 0)}. "
        f"Average risk score: {data.get('avg_risk_score', 0)}."
    )

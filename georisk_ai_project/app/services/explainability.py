def generate_insights(row):
    insights = []

    risk_score = row.get("risk_score", 0)
    failure_prob = row.get("failure_probability", 0)
    anomaly = row.get("anomaly_score_model", 0)
    strain = row.get("strain_rate", 0)

    if risk_score > 0.75:
        insights.append("High composite risk level")

    if failure_prob > 0.6:
        insights.append("Elevated failure probability signal")

    if anomaly > 0.6:
        insights.append("Significant anomaly pattern detected")

    if strain > 0.6:
        insights.append("Elevated strain rate observed")

    if not insights:
        insights.append("No significant deviations detected")

    return insights
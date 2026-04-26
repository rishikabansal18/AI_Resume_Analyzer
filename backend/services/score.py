def calculate_score(similarity, matched, total_required):
    skill_score = len(matched) / total_required if total_required else 0

    final_score = (
        0.6 * similarity +
        0.4 * skill_score
    ) * 100

    return round(final_score, 2)
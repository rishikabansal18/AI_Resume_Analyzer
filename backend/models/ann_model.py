import numpy as np

# No heavy training (kept lightweight for deployment)
def train_model():
    return None


def predict_score(model, similarity, ratio):
    """
    similarity: text similarity (0–1)
    ratio: matched_skills / total_skills (0–1)
    """

    # Weighted scoring (acts like ANN replacement)
    score = (0.6 * similarity) + (0.4 * ratio)

    # Ensure bounds
    return max(0, min(score, 1))
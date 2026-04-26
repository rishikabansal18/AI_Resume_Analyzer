from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# load model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_similarity(resume_text, job_desc):
    embeddings = model.encode([resume_text, job_desc])

    score = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return float(score)
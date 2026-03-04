from sentence_transformers import util
from models.nlp_model import get_embedding

def check_similarity(regulation, policy):

    emb1 = get_embedding(regulation)
    emb2 = get_embedding(policy)

    score = util.cos_sim(emb1, emb2)

    return float(score)
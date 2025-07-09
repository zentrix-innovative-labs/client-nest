import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class CollaborativeRecommender:
    def __init__(self, user_item_matrix):
        self.user_item_matrix = user_item_matrix

    def recommend(self, user_id, top_k=5):
        user_vector = self.user_item_matrix[user_id]
        similarities = cosine_similarity([user_vector], self.user_item_matrix)[0]
        similar_users = np.argsort(similarities)[::-1][1:top_k+1]
        recommended_items = set()
        for u in similar_users:
            items = np.where(self.user_item_matrix[u] > 0)[0]
            recommended_items.update(items)
        return list(recommended_items)[:top_k]

class ContentBasedRecommender:
    def __init__(self, item_features):
        self.item_features = item_features

    def recommend(self, user_profile, top_k=5):
        similarities = cosine_similarity([user_profile], self.item_features)[0]
        recommended_items = np.argsort(similarities)[::-1][:top_k]
        return recommended_items.tolist()

class HybridRecommender:
    def __init__(self, collaborative, content_based, alpha=0.5):
        self.collaborative = collaborative
        self.content_based = content_based
        self.alpha = alpha

    def recommend(self, user_id, user_profile, top_k=5):
        collab_scores = np.zeros(self.content_based.item_features.shape[0])
        collab_items = self.collaborative.recommend(user_id, top_k=top_k*2)
        collab_scores[collab_items] = 1
        content_scores = cosine_similarity([user_profile], self.content_based.item_features)[0]
        hybrid_scores = self.alpha * collab_scores + (1 - self.alpha) * content_scores
        recommended_items = np.argsort(hybrid_scores)[::-1][:top_k]
        return recommended_items.tolist() 
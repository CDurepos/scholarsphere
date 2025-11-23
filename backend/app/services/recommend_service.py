from backend.app.db.procedures import sql_recommend


def recommend_collaborators(user_id: int):
    return sql_recommend(user_id)

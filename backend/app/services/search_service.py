from backend.app.db.procedures import sql_search


def search_users(query: str):
    return sql_search(query)

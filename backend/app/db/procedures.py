from backend.app.db.connection import get_connection


def sql_search(query):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.callproc("search_faculty", [query])
    result = cursor.stored_results().pop().fetchall()
    cursor.close()
    conn.close()
    return result


def sql_recommend(user_id):
    # conn = get_connection()
    # cursor = conn.cursor(dictionary=True)
    # cursor.callproc("", [user_id])
    # result = cursor.stored_results().pop().fetchall()
    # cursor.close()
    # conn.close()
    # return result
    return []

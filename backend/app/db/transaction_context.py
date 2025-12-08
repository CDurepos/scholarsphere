# Aidan

from backend.app.db.connection import get_connection

from typing import Final


class TransactionContext:
    """
    Provides a transaction object for the service layer to pass to the database layer.

    This class allows the service layer to perform multiple database operations
    as a single atomic transaction. It abstracts the underlying connection so
    that the service layer can commit or rollback changes without needing to
    know connector-specific details. This also makes it easier to swap out
    the database connector in the future if needed.

    Example usage:
    with start_transaction() as transaction_context:
        sql_create_faculty_generates_keyword(transaction_context, generation_id, faculty_id, datetime.now())
    """

    def __init__(self, conn):
        self._conn: Final = conn
        self._cursor: Final = conn.cursor(dictionary=True)

    @property
    def conn(self) -> Final:
        return self._conn

    @property
    def cursor(self) -> Final:
        return self._cursor

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._cursor.close()
        self._conn.close()

    # --- Context manager methods ---
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.commit()  # commit if everything went fine
            else:
                self.rollback()  # rollback if an exception occurred
        finally:
            self.close()
        return False


def start_transaction(conn=None):
    if conn is None:
        conn = get_connection()
    return TransactionContext(conn)

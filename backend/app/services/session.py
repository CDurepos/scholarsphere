"""
Author: Clayton Durepos
"""

"""
Session service for managing refresh tokens and sessions.
"""
import hashlib
import secrets
import uuid
import datetime
from backend.app.db.transaction_context import start_transaction
from backend.app.db.procedures import (
    sql_create_session,
    sql_read_session_by_token_hash,
    sql_read_session_by_faculty,
    sql_update_session,
)
from backend.app.config import Config


def generate_refresh_token() -> str:
    """
    Generate a cryptographically secure random refresh token.
    
    Returns:
        str: Random token string (256 bits = 32 bytes = 64 hex characters)
    """
    return secrets.token_hex(32)  # 32 bytes = 64 hex characters


def hash_token(token: str) -> str:
    """
    Hash a refresh token using SHA-256.
    
    Args:
        token: Raw refresh token string
    
    Returns:
        str: SHA-256 hash (64 hex characters)
    """
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def create_session(faculty_id: str, remember_me: bool = False) -> tuple:
    """
    Create a new session with a refresh token.
    
    Args:
        faculty_id: UUID of the faculty member
        remember_me: If True, use extended expiration (30 days), else use default (7 days)
    
    Returns:
        tuple: (refresh_token, session_id, expiration_days)
            - refresh_token: Raw refresh token to send to client (store in HttpOnly cookie)
            - session_id: UUID of the created session
            - expiration_days: Number of days until expiration
    """
    try:
        with start_transaction() as transaction_context:
            # Generate refresh token and hash
            refresh_token = generate_refresh_token()
            token_hash = hash_token(refresh_token)
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Calculate expiration based on remember_me flag
            expiration_days = (
                30
                if remember_me 
                else 7
            )
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=expiration_days)
            
            # Create session record
            sql_create_session(
                transaction_context,
                session_id,
                faculty_id,
                token_hash,
                expires_at
            )
            
            # Transaction commits automatically on success
        
        return refresh_token, session_id, expiration_days
    except Exception as e:
        # Transaction already rolled back by context manager
        raise e


def get_session_by_token_hash(token_hash: str) -> dict | None:
    """
    Retrieve a session by its token hash.
    
    Only returns active (non-revoked, non-expired) sessions.
    
    Args:
        token_hash: SHA-256 hash of the refresh token
    
    Returns:
        dict | None: Session record with faculty_id, or None if not found/invalid
    """
    try:
        with start_transaction() as transaction_context:
            session = sql_read_session_by_token_hash(transaction_context, token_hash)
            return session
    except Exception as e:
        raise e


def revoke_session(token_hash: str) -> bool:
    """
    Revoke a session by its token hash.
    
    Args:
        token_hash: SHA-256 hash of the refresh token
    
    Returns:
        bool: True if session was revoked, False if not found
    """
    try:
        with start_transaction() as transaction_context:
            rows_affected = sql_update_session(
                transaction_context,
                token_hash=token_hash,
                revoked=True
            )
            # Transaction commits automatically on success
            return rows_affected > 0
    except Exception as e:
        # Transaction already rolled back by context manager
        raise e


def revoke_all_sessions(faculty_id: str) -> int:
    """
    Revoke all active sessions for a faculty member.
    
    Args:
        faculty_id: UUID of the faculty member
    
    Returns:
        int: Number of sessions revoked
    """
    try:
        with start_transaction() as transaction_context:
            rows_affected = sql_update_session(
                transaction_context,
                faculty_id=faculty_id,
                revoked=True
            )
            # Transaction commits automatically on success
            return rows_affected
    except Exception as e:
        # Transaction already rolled back by context manager
        raise e

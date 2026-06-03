from datetime import datetime

from sqlalchemy.orm import Session

from app.models.token import RefreshToken


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        self.db.add(refresh_token)
        return refresh_token

    def get_active_by_hash(self, token_hash: str) -> RefreshToken | None:
        return (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > datetime.utcnow(),
            )
            .first()
        )

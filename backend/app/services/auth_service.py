from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    refresh_token_expires_at,
    verify_password,
)
from app.models.token import RefreshToken
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.subscription_service import SubscriptionService


class AuthenticationError(Exception):
    pass


class AccountLockedError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class AuthService:
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15

    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.tokens = TokenRepository(db)
        self.subscriptions = SubscriptionService(db)

    def register(self, payload: RegisterRequest) -> TokenResponse:
        existing_user = self.users.get_by_email(payload.email)
        if existing_user:
            raise UserAlreadyExistsError("A user with this email already exists")

        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name.strip(),
            hashed_password=hash_password(payload.password),
        )
        self.users.add(user)
        self.db.flush()
        self.subscriptions.ensure_free_subscription(user.id)
        self.db.commit()
        self.db.refresh(user)
        return self._issue_token_pair(user)

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(payload.email)
        if not user:
            raise AuthenticationError("Invalid email or password")
        self._raise_if_locked(user)
        if not user.is_active:
            raise AuthenticationError("Account is disabled")

        if not verify_password(payload.password, user.hashed_password):
            self._record_failed_login(user)
            self.db.commit()
            raise AuthenticationError("Invalid email or password")

        user.failed_login_attempts = 0
        user.locked_until = None
        self.db.commit()
        self.db.refresh(user)
        return self._issue_token_pair(user)

    def refresh(self, refresh_token: str) -> TokenResponse:
        token_hash = hash_refresh_token(refresh_token)
        stored_token = self.tokens.get_active_by_hash(token_hash)
        if not stored_token or not stored_token.user or not stored_token.user.is_active:
            raise AuthenticationError("Invalid refresh token")

        stored_token.revoked = True
        stored_token.revoked_at = datetime.utcnow()
        self.db.commit()
        return self._issue_token_pair(stored_token.user)

    def logout(self, refresh_token: str) -> None:
        stored_token = self.tokens.get_active_by_hash(hash_refresh_token(refresh_token))
        if stored_token:
            stored_token.revoked = True
            stored_token.revoked_at = datetime.utcnow()
            self.db.commit()

    def _issue_token_pair(self, user: User) -> TokenResponse:
        refresh_token = create_refresh_token()
        stored_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=refresh_token_expires_at(),
        )
        self.tokens.add_refresh_token(stored_token)
        self.db.commit()
        self.db.refresh(user)
        access_token = create_access_token(
            subject=str(user.id),
            claims={"role": user.role.value, "email": user.email},
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            user=user,
        )

    def _raise_if_locked(self, user: User) -> None:
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise AccountLockedError("Account is temporarily locked")

    def _record_failed_login(self, user: User) -> None:
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= self.MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=self.LOCKOUT_MINUTES)

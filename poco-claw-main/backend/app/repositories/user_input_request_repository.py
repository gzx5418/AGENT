import uuid

from sqlalchemy.orm import Session

from app.models.agent_session import AgentSession
from app.models.user_input_request import UserInputRequest


class UserInputRequestRepository:
    @staticmethod
    def create(session_db: Session, request: UserInputRequest) -> UserInputRequest:
        session_db.add(request)
        return request

    @staticmethod
    def get_by_id(session_db: Session, request_id: str) -> UserInputRequest | None:
        return (
            session_db.query(UserInputRequest)
            .filter(UserInputRequest.id == request_id)
            .first()
        )

    @staticmethod
    def list_pending_by_session(
        session_db: Session, session_id: uuid.UUID
    ) -> list[UserInputRequest]:
        return (
            session_db.query(UserInputRequest)
            .filter(UserInputRequest.session_id == session_id)
            .filter(UserInputRequest.status == "pending")
            .order_by(UserInputRequest.created_at.asc())
            .all()
        )

    @staticmethod
    def list_pending_by_user(
        session_db: Session, user_id: str, session_id: uuid.UUID | None = None
    ) -> list[UserInputRequest]:
        query = (
            session_db.query(UserInputRequest)
            .join(AgentSession, UserInputRequest.session_id == AgentSession.id)
            .filter(AgentSession.user_id == user_id)
            .filter(UserInputRequest.status == "pending")
        )
        if session_id:
            query = query.filter(UserInputRequest.session_id == session_id)
        return query.order_by(UserInputRequest.created_at.asc()).all()

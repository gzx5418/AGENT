import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.agent_message import AgentMessage
from app.models.agent_session import AgentSession
from app.models.project import Project


class SearchRepository:
    """Data access layer for lightweight global search."""

    @staticmethod
    def _build_pattern(query: str) -> str:
        return f"%{query.lower()}%"

    @classmethod
    def search_sessions_by_title(
        cls,
        session_db: Session,
        *,
        user_id: str,
        query: str,
        limit: int,
        project_id: uuid.UUID | None = None,
        kind: str = "chat",
    ) -> list[AgentSession]:
        pattern = cls._build_pattern(query)
        q = session_db.query(AgentSession).filter(
            AgentSession.user_id == user_id,
            AgentSession.is_deleted.is_(False),
            AgentSession.kind == kind,
            AgentSession.title.isnot(None),
        )
        if project_id is not None:
            q = q.filter(AgentSession.project_id == project_id)
        return (
            q.filter(func.lower(AgentSession.title).like(pattern))
            .order_by(AgentSession.updated_at.desc())
            .limit(limit)
            .all()
        )

    @classmethod
    def search_projects_by_name(
        cls,
        session_db: Session,
        *,
        user_id: str,
        query: str,
        limit: int,
    ) -> list[Project]:
        pattern = cls._build_pattern(query)
        return (
            session_db.query(Project)
            .filter(
                Project.user_id == user_id,
                Project.is_deleted.is_(False),
            )
            .filter(func.lower(Project.name).like(pattern))
            .order_by(Project.updated_at.desc())
            .limit(limit)
            .all()
        )

    @classmethod
    def search_messages_by_preview(
        cls,
        session_db: Session,
        *,
        user_id: str,
        query: str,
        limit: int,
        project_id: uuid.UUID | None = None,
        kind: str = "chat",
    ) -> list[AgentMessage]:
        pattern = cls._build_pattern(query)
        q = (
            session_db.query(AgentMessage)
            .join(AgentSession, AgentMessage.session_id == AgentSession.id)
            .filter(
                AgentSession.user_id == user_id,
                AgentSession.is_deleted.is_(False),
                AgentSession.kind == kind,
                AgentMessage.text_preview.isnot(None),
            )
        )
        if project_id is not None:
            q = q.filter(AgentSession.project_id == project_id)
        return (
            q.filter(func.lower(AgentMessage.text_preview).like(pattern))
            .order_by(AgentMessage.created_at.desc())
            .limit(limit)
            .all()
        )

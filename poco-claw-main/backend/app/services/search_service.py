import uuid

from sqlalchemy.orm import Session

from app.repositories.search_repository import SearchRepository
from app.schemas.search import (
    GlobalSearchResponse,
    SearchMessageResult,
    SearchProjectResult,
    SearchTaskResult,
)


class SearchService:
    """Service layer for lightweight global search."""

    _MAX_LIMIT = 20

    @classmethod
    def _clamp_limit(cls, value: int) -> int:
        return max(0, min(int(value), cls._MAX_LIMIT))

    def search(
        self,
        db: Session,
        *,
        user_id: str,
        query: str,
        limit_tasks: int = 10,
        limit_projects: int = 5,
        limit_messages: int = 10,
        project_id: uuid.UUID | None = None,
    ) -> GlobalSearchResponse:
        clean_query = (query or "").strip()
        if not clean_query:
            return GlobalSearchResponse(query="", tasks=[], projects=[], messages=[])

        tasks_limit = self._clamp_limit(limit_tasks)
        projects_limit = self._clamp_limit(limit_projects)
        messages_limit = self._clamp_limit(limit_messages)

        sessions = (
            SearchRepository.search_sessions_by_title(
                db,
                user_id=user_id,
                query=clean_query,
                limit=tasks_limit,
                project_id=project_id,
                kind="chat",
            )
            if tasks_limit > 0
            else []
        )
        projects = (
            SearchRepository.search_projects_by_name(
                db,
                user_id=user_id,
                query=clean_query,
                limit=projects_limit,
            )
            if projects_limit > 0
            else []
        )
        messages = (
            SearchRepository.search_messages_by_preview(
                db,
                user_id=user_id,
                query=clean_query,
                limit=messages_limit,
                project_id=project_id,
                kind="chat",
            )
            if messages_limit > 0
            else []
        )

        return GlobalSearchResponse(
            query=clean_query,
            tasks=[
                SearchTaskResult(
                    session_id=s.id,
                    title=s.title,
                    status=s.status,
                    timestamp=s.updated_at,
                )
                for s in sessions
            ],
            projects=[
                SearchProjectResult(
                    project_id=p.id,
                    name=p.name,
                )
                for p in projects
            ],
            messages=[
                SearchMessageResult(
                    message_id=m.id,
                    session_id=m.session_id,
                    text_preview=m.text_preview or "",
                    timestamp=m.created_at,
                )
                for m in messages
                if m.text_preview
            ],
        )

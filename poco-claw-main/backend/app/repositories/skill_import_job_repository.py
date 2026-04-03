import uuid

from sqlalchemy.orm import Session

from app.models.skill_import_job import SkillImportJob


class SkillImportJobRepository:
    """Data access layer for skill import jobs."""

    @staticmethod
    def create(
        session_db: Session,
        *,
        user_id: str,
        archive_key: str,
        selections: list[dict],
    ) -> SkillImportJob:
        job = SkillImportJob(
            user_id=user_id,
            archive_key=archive_key,
            selections=selections,
            status="queued",
            progress=0,
        )
        session_db.add(job)
        return job

    @staticmethod
    def get_by_id(session_db: Session, job_id: uuid.UUID) -> SkillImportJob | None:
        return (
            session_db.query(SkillImportJob).filter(SkillImportJob.id == job_id).first()
        )

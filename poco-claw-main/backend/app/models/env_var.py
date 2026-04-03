from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class UserEnvVar(Base, TimestampMixin):
    __tablename__ = "user_env_vars"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value_ciphertext: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scope: Mapped[str] = mapped_column(String(50), default="user", nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "key", name="uq_user_env_vars_user_key"),
    )

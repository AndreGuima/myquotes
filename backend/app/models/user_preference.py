from database import Base
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Ex: "notifications", "theme", "habits"
    category = Column(String(50), nullable=False)

    # Preferências flexíveis por categoria
    preferences = Column(JSON, nullable=False)

    created_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "category",
            name="uq_user_preferences_user_category",
        ),
    )

    # Relacionamento (opcional, mas útil)
    user = relationship(
        "User",
        backref="preferences",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<UserPreference user_id={self.user_id} " f"category={self.category}>"

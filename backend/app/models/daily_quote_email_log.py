from database import Base
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, func


class DailyQuoteEmailLog(Base):
    __tablename__ = "daily_quote_email_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    date = Column(Date, nullable=False)
    sent_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

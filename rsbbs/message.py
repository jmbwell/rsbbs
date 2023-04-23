from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Message(Base):
    __tablename__ = 'message'
    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[str] = mapped_column(String)
    recipient: Mapped[str] = mapped_column(String)
    subject: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    datetime: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    is_private: Mapped[bool] = mapped_column(Boolean)


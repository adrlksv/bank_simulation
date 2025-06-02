from datetime import datetime
from sqlalchemy import DateTime, Integer, Numeric, String, ForeignKey, Float, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Account(Base):
    __tablename__ = "account"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        index=True,
    )
    bank_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bank.id"),
        nullable=False,
    )
    client_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("client.id"),
        nullable=False,
    )
    balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

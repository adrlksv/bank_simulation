from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    DateTime, 
    Integer,
    ForeignKey,  
    func, 
    DECIMAL as SQLAlchemyDecimal
)
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
    balance: Mapped[Decimal] = mapped_column(SQLAlchemyDecimal(12, 2), default=Decimal("0.00"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

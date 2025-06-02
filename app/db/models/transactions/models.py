from datetime import datetime
from sqlalchemy import JSON, DateTime, Integer, ForeignKey, Numeric, Enum as SQLAlchemyEnum, func
from sqlalchemy.orm import Mapped, mapped_column

from enum import Enum

from app.db.database import Base


class TransactionType(str, Enum):
    deposit = "deposit"
    withdraw = "withdRaw"
    transfer = "transfer"


class OperationType(str, Enum):
    create_account = "create_account"
    close_account = "close_account"
    deposit = "deposit"
    withdraw = "withdraw"
    transfer = "transfer"


class Transaction(Base):
    __tablename__ = "transaction"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        index=True,
    )
    from_account_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("account.id"),
        nullable=True,
    )
    to_account_id: Mapped[int| None] = mapped_column(
        Integer,
        ForeignKey("account.id"),
        nullable=True,
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    type: Mapped[Enum] = mapped_column(SQLAlchemyEnum(TransactionType), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default = func.now(), nullable=False)


class OperationLog(Base):
    __tablename__ = "operation_log"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("account.id"),
        nullable=False,
    )
    action: Mapped[Enum] = mapped_column(SQLAlchemyEnum(OperationType), nullable=False)
    timestampe: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    data: Mapped[dict] = mapped_column(JSON)

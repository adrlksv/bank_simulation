from decimal import Decimal
from sqlalchemy import Integer, Numeric, ForeignKey, DECIMAL as SQLAlchemyDecimal
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Branch(Base):
    __tablename__ = "branch"
    
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
    balance: Mapped[Decimal] = mapped_column(
        SQLAlchemyDecimal(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

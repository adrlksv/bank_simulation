from decimal import Decimal
from sqlalchemy import Integer, Numeric, String, DECIMAL as SQLAlchemyDecimal
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Bank(Base):
    __tablename__ = "bank"
    
    id: Mapped[int] = mapped_column(
        primary_key=True, 
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )
    comission_income: Mapped[Decimal] = mapped_column(SQLAlchemyDecimal(12, 2), default=Decimal("0.00"), nullable=False)
